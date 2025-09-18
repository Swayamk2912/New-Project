from .models import Message
from proposals.models import Proposal # Import Proposal model
from notifications.models import Notification # Import Notification model

def notification_counts(request):
    if request.user.is_authenticated:
        unread_messages = Message.objects.filter(receiver=request.user, is_read=False).count()
        unread_proposals = 0
        unread_app_notifications = Notification.objects.filter(user=request.user, is_read=False).count()

        if request.user.role == 'client':
            # Client sees unread proposals for their jobs
            unread_proposals = Proposal.objects.filter(
                job__client=request.user,
                is_read_by_client=False
            ).count()
        elif request.user.role == 'freelancer':
            # Freelancer sees unread status updates for their proposals
            unread_proposals = Proposal.objects.filter(
                freelancer=request.user,
                is_read_by_freelancer=False
            ).exclude(status='pending').count() # Exclude pending as they are not "updates" yet

        return {
            'unread_messages': unread_messages,
            'unread_proposals': unread_proposals,
            'unread_app_notifications': unread_app_notifications,
            'total_notifications': unread_messages + unread_proposals + unread_app_notifications
        }
    return {
        'unread_messages': 0,
        'unread_proposals': 0,
        'unread_app_notifications': 0,
        'total_notifications': 0
    }
