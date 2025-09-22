import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Conversation, Message

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

        if message_type == 'chat_message':
            message_content = text_data_json['message']
            sender_username = text_data_json['sender']

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
