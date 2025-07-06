from django.db import models
from .support_agent_model import SfSupportAgent
from .ticket_model import SfTicket


class SfRagMessage(models.Model) :
    message_text = models.TextField(default="message")
    staff = models.ForeignKey(SfSupportAgent, null=True, on_delete=models.SET_NULL)
    ticket = models.ForeignKey(SfTicket, null=True, on_delete=models.SET_NULL)
    def __str__(self) : 
        return self.message_text
    
    class Meta:
        db_table = 'sfix_rag_message'