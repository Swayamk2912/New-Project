from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Conversation, Message
from django.db.models import Q
from users.models import User
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import ConversationSerializer, MessageSerializer

@login_required
def inbox(request):
    user = request.user
    conversations = Conversation.objects.filter(participants=user).order_by('-updated_at')
    return render(request, 'messaging/inbox.html', {'conversations': conversations})

@login_required
def conversation_detail(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
    messages = conversation.messages.all().order_by('timestamp')

    # Mark all unread messages in this conversation as read for the current user
    conversation.messages.filter(receiver=request.user, is_read=False).update(is_read=True)

    return render(request, 'messaging/chat.html', {'conversation': conversation, 'messages': messages})

@login_required
def start_conversation(request, user_id):
    recipient = get_object_or_404(User, id=user_id)
    user = request.user

    if user == recipient:
        # Optionally handle this case, e.g., redirect to inbox with a message
        return redirect('messaging:inbox')

    # Find existing conversation or create a new one
    conversation = Conversation.objects.filter(
        Q(participants=user) & Q(participants=recipient)
    ).distinct().first()

    if not conversation:
        conversation = Conversation.objects.create()
        conversation.participants.add(user, recipient)
        conversation.save()

    return redirect('messaging:conversation_detail', conversation_id=conversation.id)
