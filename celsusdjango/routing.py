from django.urls import re_path

from celsusdjango.consumers import CurtainConsumer

websocket_urlpatterns = [
    re_path(r'ws/curtain/(?P<session_id>\w+)/(?P<personal_id>\w+)/$', CurtainConsumer.as_asgi()),
]