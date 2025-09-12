from django.db.models.signals import post_save
from django.dispatch import receiver
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
