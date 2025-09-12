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
        data = json.loads(text_data)
        content = data.get('content')
        sender_id = self.scope['user'].id

        # persist message
        message = await database_sync_to_async(self.create_message)(sender_id, content)

        payload = {
            'id': message.id,
            'sender_id': sender_id,
            'content': message.content,
            'timestamp': message.timestamp.isoformat()
        }

        # broadcast to group
        await self.channel_layer.group_send(self.room_group_name, {
            'type': 'chat.message',
            'message': payload
        })

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event['message']))

    def create_message(self, sender_id, content):
        conv = Conversation.objects.get(id=self.conversation_id)
        sender = User.objects.get(id=sender_id)
        return Message.objects.create(conversation=conv, sender=sender, content=content)
