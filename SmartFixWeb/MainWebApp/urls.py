from django.urls import path
from . import views

urlpatterns = [
    path('', views.default_view, name='default'),
    path('chat/', views.chat_request, name='chat_request'),
]