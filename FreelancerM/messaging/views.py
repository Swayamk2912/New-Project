from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Conversation, Message
from django.db.models import Q
from users.models import User
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import ConversationSerializer, MessageSerializer
import json
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.http import JsonResponse
from django.views.decorators.http import require_POST

@login_required
def inbox(request):
    user = request.user
    conversations = Conversation.objects.filter(participants=user, is_deleted=False).order_by('-updated_at')
    return render(request, 'messaging/inbox.html', {'conversations': conversations})

@login_required
def conversation_detail(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user, is_deleted=False)
    messages = conversation.messages.filter(is_deleted=False).order_by('timestamp')

    # Mark all unread messages in this conversation as read for the current user
    conversation.messages.filter(receiver=request.user, is_read=False).update(is_read=True)

    job = None
    if messages.exists() and messages.first().job:
        job = messages.first().job

    return render(request, 'messaging/chat.html', {'conversation': conversation, 'messages': messages, 'job': job})

@login_required
def start_conversation(request, user_id):
    recipient = get_object_or_404(User, id=user_id)
    user = request.user

    if user == recipient:
        # Optionally handle this case, e.g., redirect to inbox with a message
        return redirect('messaging:inbox')

    # Find existing conversation or create a new one
    conversation = Conversation.objects.filter(
        Q(participants=user) & Q(participants=recipient),
        is_deleted=False
    ).distinct().first()

    if not conversation:
        conversation = Conversation.objects.create()
        conversation.participants.add(user, recipient)
        conversation.save()

    return redirect('messaging:conversation_detail', conversation_id=conversation.id)

@login_required
@require_POST
def delete_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)

    if message.sender != request.user:
        return JsonResponse({'status': 'error', 'message': 'You can only delete your own messages.'}, status=403)

    message.is_deleted = True
    message.save()

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"chat_{message.conversation.id}",
        {
            'type': 'message_deleted',
            'message_id': message.id,
            'timestamp': message.timestamp.isoformat(),
        }
    )
    return redirect('messaging:inbox')

@login_required
@require_POST
def delete_conversation(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id)

    if request.user not in conversation.participants.all():
        return JsonResponse({'status': 'error', 'message': 'You are not a participant in this conversation.'}, status=403)

    conversation.is_deleted = True
    conversation.save()
    conversation.messages.all().update(is_deleted=True) # Mark all messages as deleted too

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"chat_{conversation.id}",
        {
            'type': 'conversation_deleted',
            'conversation_id': conversation.id,
        }
    )
    return redirect('messaging:inbox')
