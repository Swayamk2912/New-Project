import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Notification
from messaging.models import Message
from proposals.models import Proposal

User = get_user_model()

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_authenticated:
            self.user_id = self.scope["user"].id
            self.room_group_name = f'notifications_{self.user_id}'

            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        if self.scope["user"].is_authenticated:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json.get('action')

        if action == 'mark_read':
            notification_id = text_data_json.get('notification_id')
            if notification_id:
                await self.mark_notification_as_read(notification_id)
                unread_count = await self.get_unread_notifications_count(self.scope["user"])
                await self.send(text_data=json.dumps({
                    'action': 'unread_count_update',
                    'unread_count': unread_count
                }))
        elif action == 'mark_all_read':
            await self.mark_all_notifications_as_read(self.scope["user"])
            await self.mark_all_messages_as_read(self.scope["user"])
            await self.mark_all_proposals_as_read(self.scope["user"])
            unread_count = await self.get_unread_notifications_count(self.scope["user"]) # This now gets total unread
            await self.send(text_data=json.dumps({
                'action': 'unread_count_update',
                'unread_count': unread_count
            }))
        elif action == 'get_unread_count':
            unread_count = await self.get_unread_notifications_count(self.scope["user"])
            await self.send(text_data=json.dumps({
                'action': 'unread_count_update',
                'unread_count': unread_count
            }))

    async def send_notification(self, event):
        message = event['message']
        await self.send(text_data=json.dumps(message))

    @database_sync_to_async
    def get_unread_notifications_count(self, user):
        return Notification.objects.filter(user=user, is_read=False).count()

    @database_sync_to_async
    def mark_notification_as_read(self, notification_id):
        try:
            notification = Notification.objects.get(id=notification_id, user=self.scope["user"])
            notification.is_read = True
            notification.save()
        except Notification.DoesNotExist:
            pass

    @database_sync_to_async
    def mark_all_notifications_as_read(self, user):
        Notification.objects.filter(user=user, is_read=False).update(is_read=True)

    @database_sync_to_async
    def mark_all_messages_as_read(self, user):
        Message.objects.filter(receiver=user, is_read=False).update(is_read=True)

    @database_sync_to_async
    def mark_all_proposals_as_read(self, user):
        # For client, mark proposals received as read
        Proposal.objects.filter(job__client=user, is_read_by_client=False).update(is_read_by_client=True)
        # For freelancer, mark proposals updates as read
        Proposal.objects.filter(freelancer=user, is_read_by_freelancer=False).update(is_read_by_freelancer=True)
