from django.urls import path
from .views import show_default_view, show_chat_view, new_ticket

urlpatterns = [
    path(route='', view=show_default_view, name='default'),
    path(route='chat/', view=show_chat_view, name='chat'),
    path(route='new_ticket/', view=new_ticket, name='new_ticket'),
]