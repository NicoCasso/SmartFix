from django.urls import path
from . import views

urlpatterns = [
    path('', views.default_view, name='default'),
    path('chat_ticket/', views.chat_ticket_view, name='chat_ticket'),
    path('chat/', views.chat_view, name='chat'),
]