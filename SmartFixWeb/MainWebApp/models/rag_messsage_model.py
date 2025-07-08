from django.db import models
from .support_agent_model import SfSupportAgent
from .ticket_model import SfTicket


class SfRagMessage(models.Model) :
    text = models.TextField(default="message")
    author = models.ForeignKey(SfSupportAgent, null=True, on_delete=models.SET_NULL)
    ticket = models.ForeignKey(SfTicket, null=True, on_delete=models.SET_NULL)
    created = models.DateTimeField(auto_now_add=True)
    def __str__(self) : 
        return self.text
    
    class Meta:
        db_table = 'sfix_rag_message'