from django.contrib import admin
from django.urls import path, include

from shopChat.views import shop_chat

urlpatterns = [
    path("", shop_chat, name="shop_chat"),
]