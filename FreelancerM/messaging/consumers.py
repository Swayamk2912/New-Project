import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Conversation, Message, Call
from django.utils import timezone

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f'chat_{self.conversation_id}'

        # optionally check user permissions
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')
        sender_username = text_data_json.get('sender')

        if message_type == 'chat_message':
            message_content = text_data_json['message']
            
            sender = await self.get_user(sender_username)
            conversation = await self.get_conversation(self.conversation_id)
            
            # Get the receiver from the conversation
            receiver = await self.get_receiver(conversation, sender)

            new_message = await self.save_message(conversation, sender, receiver, message_content)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message_content,
                    'sender': sender_username,
                    'message_id': new_message.id,
                    'timestamp': new_message.timestamp.isoformat(),
                }
            )
        elif message_type == 'call_initiate':
            sender = await self.get_user(sender_username)
            conversation = await self.get_conversation(self.conversation_id)
            receiver = await self.get_receiver(conversation, sender)
            call = await self.create_call(conversation, sender, receiver)

            # Send to chat room
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'call_initiate',
                    'call_id': call.id,
                    'sender': sender_username,
                }
            )
            # Send to receiver's notification group
            await self.channel_layer.group_send(
                f'user_{receiver.id}',
                {
                    'type': 'incoming_call',
                    'caller': sender.username,
                    'conversation_id': self.conversation_id
                }
            )
        elif message_type in ['call_accept', 'call_reject', 'call_end']:
            call_id = text_data_json.get('call_id')
            status = {
                'call_accept': 'accepted',
                'call_reject': 'rejected',
                'call_end': 'ended'
            }[message_type]
            await self.update_call_status(call_id, status)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'call_status',
                    'status': status,
                    'call_id': call_id,
                    'sender': sender_username,
                }
            )
        elif message_type in ['webrtc_offer', 'webrtc_answer', 'webrtc_ice_candidate']:
            payload = text_data_json
            payload['type'] = message_type
            payload['sender'] = sender_username
            await self.channel_layer.group_send(
                self.room_group_name,
                payload
            )

    async def call_initiate(self, event):
        await self.send(text_data=json.dumps(event))

    async def call_accept(self, event):
        await self.send(text_data=json.dumps(event))

    async def call_reject(self, event):
        await self.send(text_data=json.dumps(event))

    async def call_end(self, event):
        await self.send(text_data=json.dumps(event))

    async def webrtc_offer(self, event):
        await self.send(text_data=json.dumps(event))

    async def webrtc_answer(self, event):
        await self.send(text_data=json.dumps(event))

    async def webrtc_ice_candidate(self, event):
        await self.send(text_data=json.dumps(event))

    async def call_status(self, event):
        await self.send(text_data=json.dumps(event))

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        message_id = event['message_id']
        timestamp = event['timestamp']

        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': message,
            'sender': sender,
            'message_id': message_id,
            'timestamp': timestamp,
        }))

    async def message_deleted(self, event):
        message_id = event['message_id']
        timestamp = event['timestamp']

        await self.send(text_data=json.dumps({
            'type': 'message_deleted',
            'message_id': message_id,
            'timestamp': timestamp,
        }))

    async def conversation_deleted(self, event):
        conversation_id = event['conversation_id']

        await self.send(text_data=json.dumps({
            'type': 'conversation_deleted',
            'conversation_id': conversation_id,
        }))

    @database_sync_to_async
    def get_user(self, username):
        return User.objects.get(username=username)

    @database_sync_to_async
    def get_conversation(self, conversation_id):
        return Conversation.objects.get(id=conversation_id)
    
    @database_sync_to_async
    def get_receiver(self, conversation, sender):
        return conversation.participants.exclude(id=sender.id).first()

    @database_sync_to_async
    def save_message(self, conversation, sender, receiver, content):
        return Message.objects.create(
            conversation=conversation,
            sender=sender,
            receiver=receiver,
            content=content
        )

    @database_sync_to_async
    def create_call(self, conversation, caller, receiver):
        return Call.objects.create(
            conversation=conversation,
            caller=caller,
            receiver=receiver
        )

    @database_sync_to_async
    def update_call_status(self, call_id, status):
        try:
            call = Call.objects.get(id=call_id)
            call.status = status
            if status == 'ended':
                call.end_time = timezone.now()
            call.save()
        except Call.DoesNotExist:
            print(f"Call with id {call_id} does not exist. Cannot update status.")
            # Optionally, send an error message back to the client
            # await self.channel_layer.group_send(
            #     self.room_group_name,
            #     {
            #         'type': 'call_error',
            #         'message': f"Call {call_id} not found.",
            #         'call_id': call_id,
            #     }
            # )


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            await self.close()
        else:
            self.room_group_name = f'user_{self.user.id}'
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()

    async def disconnect(self, close_code):
        if self.user.is_authenticated:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def incoming_call(self, event):
        await self.send(text_data=json.dumps({
            'type': 'incoming_call',
            'caller': event['caller'],
            'conversation_id': event['conversation_id']
        }))
