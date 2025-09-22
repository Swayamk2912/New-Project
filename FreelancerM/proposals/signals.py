from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse # Import reverse
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

        # Send email notification to the client
        client_email = job.client.email
        if client_email:
            print(f"Attempting to send email to {client_email} for job {job.title}")
            subject = f"New Proposal Received for Your Job: {job.title}"
            
            # Construct the dynamic URL
            proposal_detail_url = settings.SITE_URL + reverse('proposals:proposal_detail', args=[instance.id])

            message = (
                f"Dear {job.client.username},\n\n"
                f"A new proposal has been submitted for your job '{job.title}' by {instance.freelancer.username}.\n"
                f"You can view the proposal details here: {proposal_detail_url}\n\n"
                f"Best regards,\n"
                f"The FreelancerM Team"
            )
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [client_email],
                    fail_silently=False,
                )
                print(f"Email sent successfully to {client_email}")
            except Exception as e:
                print(f"Error sending email to {client_email}: {e}")
