import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth import get_user_model
from .models import ChatSessionMessage, ChatSession, deserialize_user

User = get_user_model()

class ChatConsumer(WebsocketConsumer):

	def connect(self):
		self.chat_room = self.scope['url_route']['kwargs']['uri']
		self.chat_group_name = f'chat_{self.chat_room}'

		# Join the chat room
		async_to_sync(self.channel_layer.group_add)(
			self.chat_group_name,
			self.channel_name
		)
		self.accept()

	def disconnect(self, close_code):
		# Leave chaat group
		async_to_sync(self.channel_layer.group_discard)(
			self.chat_group_name,
			self.channel_name
		)

	def receive(self, text_data):
		print("Received Websocket message")
		"""Create new session message"""
		data = json.loads(text_data)
		message = data['message']
		username = data['username']
		user = User.objects.filter(username=username)[0]

		uri = data['uri']
		chat_session = ChatSession.objects.get(uri=uri)

		ChatSessionMessage.objects.create(
			user=user,
			chat_session=chat_session,
			message=message
		)

		# Send message
		async_to_sync(self.channel_layer.group_send)(
			self.chat_group_name,
			{
				'type': 'send_message',
	            'status': 'SUCCESS',
	            'uri': chat_session.uri,
	            'message': message,
	            'user': deserialize_user(user)
	        }
	    )

	def send_message(self, event):
		# Send chat message to WebSocket
		self.send(text_data=json.dumps(event))
