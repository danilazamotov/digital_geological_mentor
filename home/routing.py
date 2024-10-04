# home/routing.py
from django.urls import path
from .consumers import HomeConsumer

websocket_urlpatterns = [
    path('ws/home/<str:room_name>/', HomeConsumer.as_asgi()),
]
