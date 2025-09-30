from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.urls import reverse
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Proposal
from notifications.models import Notification
from .tasks import send_proposal_notification_email_task

@receiver(post_save, sender=Proposal)
def notify_new_proposal(sender, instance, created, **kwargs):
    if created:
        job = instance.job
        proposal_detail_url = settings.SITE_URL + reverse('proposals:proposal_detail', args=[instance.id])
        
        # Create the notification
        notification = Notification.objects.create(
            user=job.client,
            verb='New proposal',
            payload={
                'proposal_id': instance.id,
                'job_id': job.id,
                'freelancer_id': instance.freelancer_id,
                'url': proposal_detail_url,
                'message': f"A new proposal has been submitted for your job '{job.title}' by {instance.freelancer.username}.",
            }
        )

        # Send notification via WebSocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'user_{job.client.id}',
            {
                'type': 'general_notification',
                'notification': {
                    'id': notification.id,
                    'verb': notification.verb,
                    'message': notification.payload.get('message'),
                    'url': notification.payload.get('url'),
                    'is_read': notification.is_read,
                    'created_at': notification.created_at.isoformat(),
                }
            }
        )
        print(f"Sent WebSocket notification to user {job.client.id}")

        # Send email notification to the client
        client_email = job.client.email
        # Enqueue email notification task to the client
        if job.client.email:
            send_proposal_notification_email_task.delay(instance.id)
            print(f"Enqueued email notification for client {job.client.email} for job {job.title}")
