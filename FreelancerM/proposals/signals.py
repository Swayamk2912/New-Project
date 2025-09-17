from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Proposal
from notifications.models import Notification

@receiver(post_save, sender=Proposal)
def notify_new_proposal(sender, instance, created, **kwargs):
    if created:
        job = instance.job
        Notification.objects.create(
            user=job.client,
            verb='New proposal',
            payload={'proposal_id': instance.id, 'job_id': job.id, 'freelancer_id': instance.freelancer_id}
        )
        channel_layer = get_channel_layer()
        group_name = f'notifications_{job.client.id}'
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'send_notification',
                'message': {
                    'verb': 'New proposal',
                    'payload': {'proposal_id': instance.id, 'job_id': job.id, 'freelancer_id': instance.freelancer_id},
                    'is_read': False,
                    'created_at': instance.created_at.isoformat()
                }
            }
        )
