from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path

from . import consumers

urlpatterns = [
    path('ws/sb<int:sbid>', consumers.Consumer.as_asgi(), name='websocket'),
]
