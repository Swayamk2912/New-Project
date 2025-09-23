import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Notification
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.conf import settings

@csrf_exempt
def notification_webhook(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get('recipient_id')
            message = data.get('message')
            notification_type = data.get('type', 'general')
            proposal_id = data.get('proposal_id')
            job_id = data.get('job_id')
            freelancer_id = data.get('freelancer_id')
            url = data.get('url')
            verb = data.get('verb', 'New Notification')

            if not user_id or not message:
                return JsonResponse({'status': 'error', 'message': 'Missing recipient_id or message'}, status=400)

            # Assuming User model is accessible via settings.AUTH_USER_MODEL
            User = settings.AUTH_USER_MODEL
            from django.apps import apps
            UserModel = apps.get_model(*User.split('.'))
            
            recipient = get_object_or_404(UserModel, id=user_id)

            Notification.objects.create(
                user=recipient,
                verb=verb,
                payload={
                    'message': message,
                    'type': notification_type,
                    'proposal_id': proposal_id,
                    'job_id': job_id,
                    'freelancer_id': freelancer_id,
                    'url': url
                }
            )
            print(f"Received webhook notification for user {user_id}: {message}")
            return JsonResponse({'status': 'success', 'message': 'Notification received'})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
        except UserModel.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Recipient user not found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Only POST requests are allowed'}, status=405)

@login_required
def unread_notification_count(request):
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'unread_count': count})

from django.shortcuts import render

@login_required
def notification_list_api(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:10] # Get latest 10
    notification_data = []
    for notification in notifications:
        # Extract message and URL from payload, or use defaults
        message = notification.payload.get('message', notification.verb)
        url = notification.payload.get('url', '#')
        
        notification_data.append({
            'id': notification.id,
            'verb': notification.verb,
            'message': message,
            'url': url,
            'is_read': notification.is_read,
            'created_at': notification.created_at.isoformat(),
        })
    return JsonResponse({'notifications': notification_data})

@login_required
def notification_list_page(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'notifications/notification_list.html', {'notifications': notifications})

@login_required
@csrf_exempt
def mark_notifications_read(request):
    if request.method == 'POST':
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return JsonResponse({'status': 'success', 'message': 'All notifications marked as read'})
    return JsonResponse({'status': 'error', 'message': 'Only POST requests are allowed'}, status=405)

@login_required
@csrf_exempt
def mark_single_notification_read(request, notification_id):
    if request.method == 'POST':
        notification = get_object_or_404(Notification, id=notification_id, user=request.user)
        notification.is_read = True
        notification.save()
        return JsonResponse({'status': 'success', 'message': 'Notification marked as read'})
    return JsonResponse({'status': 'error', 'message': 'Only POST requests are allowed'}, status=405)

@login_required
def unsubscribe_notifications(request):
    # This is a placeholder. In a real application, you would
    # implement the logic to unsubscribe the user from notifications.
    # For example, you might set a flag on the user's profile.
    # For now, we'll just return a success message.
    return JsonResponse({'status': 'success', 'message': 'Unsubscribed from notifications'})
