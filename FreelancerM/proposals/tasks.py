from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, default_retry_delay=300, max_retries=5)
def send_proposal_notification_email_task(self, proposal_id):
    from proposals.models import Proposal # Import inside task to avoid circular imports
    try:
        proposal = Proposal.objects.get(id=proposal_id)
        job = proposal.job
        client = job.client
        freelancer = proposal.freelancer

        client_email = client.email
        job_title = job.title
        freelancer_name = freelancer.get_full_name() or freelancer.username
        
        # Construct proposal URL
        proposal_url = settings.BASE_URL + reverse('proposals:proposal_detail', args=[proposal.id])

        context = {
            'client_username': client.username,
            'job_title': job_title,
            'freelancer_username': freelancer_name,
            'proposal_detail_url': proposal_url,
            'current_year': timezone.now().year,
            'unsubscribe_url': settings.BASE_URL + reverse('notifications:unsubscribe_notifications'),
        }

        subject = f"New Proposal for Your Job: {job_title}"
        html_message = render_to_string('emails/proposal_notification.html', context)
        plain_message = strip_tags(html_message) # Fallback for plain text email clients

        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [client_email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"Proposal notification email sent to {client_email} for job {job.id}")

    except Proposal.DoesNotExist:
        logger.error(f"Proposal with ID {proposal_id} not found for email notification.")
    except Exception as exc:
        logger.error(f"Failed to send proposal notification email for proposal {proposal_id}: {exc}", exc_info=True)
        self.retry(exc=exc)
