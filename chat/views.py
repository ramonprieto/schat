from django.shortcuts import render
from django.contrib.auth import get_user_model

from .models import (
    ChatSession, ChatSessionMember, ChatSessionMessage, deserialize_user
)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

# Twilio depencies
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from twilio.twiml.messaging_response import MessagingResponse


class ChatSessionView(APIView):
	"""Manage chat sessions"""

	permission_classes = (permissions.IsAuthenticated,)

	def post(self, request, *args, **kwargs):
		"""Create a new chat session"""

		user = request.user
		chat_session = ChatSession.objects.create(owner=user)

		return Response({
				'status': 'SUCCESS',
				'uri': chat_session.uri,
				'message': 'New chat session created'
			})

	def patch(self, request, *args, **kwargs):
		"""Add a user to a chat session"""

		User = get_user_model()

		uri = kwargs['uri']
		username = request.data['username']
		user = User.objects.get(username=username)

		chat_session = ChatSession.objects.get(uri=uri)
		owner = chat_session.owner

		if owner != user:
			chat_session.members.get_or_create(
				user=user,
				chat_session=chat_session
			)

		owner = deserialize_user(owner)
		members = [
			deserialize_user(chat_session.user)
			for chat_session in chat_session.members.all()
		]
		members.insert(0, owner) # Make owner the 1st member

		return Response({
			'status': 'SUCCESS',
			'members': members,
			'message': f'{user.username} joined that chat',
			'user': deserialize_user(user)
		})


class ChatSessionMessageView(APIView):
	"""Create/Get Chat session message"""

	permission_classes = (permissions.IsAuthenticated,)

	def get(self, request, *args, **kwargs):
		"""return all messages in a chat session."""
		uri = kwargs['uri']

		chat_session = ChatSession.objects.get(uri=uri)
		messages = [
			chat_session_message.to_json()
			for chat_session_message in chat_session.messages.all()
		]

		return Response({
			'id': chat_session.id,
			'uri': chat_session.uri,
			'messages': messages
		})

	def post(self, request, *args, **kwargs):
		"""Create new session message"""
		uri = kwargs['uri']
		message = request.data['message']

		user = request.user
		chat_session = ChatSession.objects.get(uri=uri)

		ChatSessionMessage.objects.create(
			user=user,
			chat_session=chat_session,
			message=message
		)

		return Response ({
            'status': 'SUCCESS',
            'uri': chat_session.uri,
            'message': message,
            'user': deserialize_user(user)
        })




