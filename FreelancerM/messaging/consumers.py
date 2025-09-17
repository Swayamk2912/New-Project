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
        message = text_data_json['message']
        sender_username = text_data_json['sender']

        sender = await self.get_user(sender_username)
        conversation = await self.get_conversation(self.conversation_id)
        
        # Get the receiver from the conversation
        receiver = await self.get_receiver(conversation, sender)

        await self.save_message(conversation, sender, receiver, message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': sender_username
            }
        )

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']

        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender
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
        print(f"Attempting to save message:")
        print(f"  Conversation: {conversation.id if conversation else 'None'}")
        print(f"  Sender: {sender.username if sender else 'None'}")
        print(f"  Receiver: {receiver.username if receiver else 'None'}")
        print(f"  Content: {content}")
        try:
            Message.objects.create(
                conversation=conversation,
                sender=sender,
                receiver=receiver,
                content=content
            )
            print("Message saved successfully!")
        except Exception as e:
            print(f"Error saving message: {e}")
