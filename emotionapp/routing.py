from django.urls import re_path
from .consumers import ClassroomConsumer

websocket_urlpatterns = [
    re_path(r'^ws/classroom/(?P<classroom_id>\d+)/$', ClassroomConsumer.as_asgi()),
]