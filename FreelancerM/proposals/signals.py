from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.urls import reverse # Import reverse
import requests # Import requests for sending HTTP POST requests
from .models import Proposal
from notifications.models import Notification
from .tasks import send_proposal_notification_email_task # Import the Celery task

@receiver(post_save, sender=Proposal)
def notify_new_proposal(sender, instance, created, **kwargs):
    if created:
        job = instance.job
        proposal_detail_url = settings.SITE_URL + reverse('proposals:proposal_detail', args=[instance.id])
        Notification.objects.create(
            user=job.client,
            verb='New proposal',
            payload={
                'proposal_id': instance.id,
                'job_id': job.id,
                'freelancer_id': instance.freelancer_id,
                'url': proposal_detail_url, # Add URL to the directly created notification
                'message': f"A new proposal has been submitted for your job '{job.title}' by {instance.freelancer.username}.", # Add message for consistency
            }
        )
        # Send webhook notification
        webhook_url = settings.SITE_URL + reverse('notifications:notification_webhook')
        notification_data = {
            "recipient_id": job.client.id,
            "message": f"A new proposal has been submitted for your job '{job.title}' by {instance.freelancer.username}.",
            "type": "new_proposal",
            "proposal_id": instance.id,
            "job_id": job.id,
            "freelancer_id": instance.freelancer_id,
            "url": settings.SITE_URL + reverse('proposals:proposal_detail', args=[instance.id]),
            "timestamp": instance.created_at.isoformat()
        }
        try:
            response = requests.post(webhook_url, json=notification_data)
            response.raise_for_status() # Raise an exception for HTTP errors
            print(f"Webhook notification sent successfully: {response.json()}")
        except requests.exceptions.RequestException as e:
            print(f"Error sending webhook notification: {e}")

        # Send email notification to the client
        client_email = job.client.email
        # Enqueue email notification task to the client
        if job.client.email:
            send_proposal_notification_email_task.delay(instance.id)
            print(f"Enqueued email notification for client {job.client.email} for job {job.title}")
