from django.urls import re_path
from chat import consumers

websocket_url_patterns = [
	re_path(r'ws/chat/(?P<uri>\w+)/$', consumers.ChatConsumer),
]