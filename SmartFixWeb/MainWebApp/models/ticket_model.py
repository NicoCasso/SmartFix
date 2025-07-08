from django.db import models
from .support_agent_model import SfSupportAgent
from .client_model import SfClient
from .worklow_model import SfWorkflow
 
class SfTicket(models.Model) :
    title = models.CharField(max_length = 128, default="new ticket")
    description = models.TextField(null=True)
    staff = models.ForeignKey(SfSupportAgent, on_delete=models.SET_NULL, null=True)
    client = models.ForeignKey(SfClient, on_delete=models.SET_NULL, null=True)
    workflow = models.ForeignKey(SfWorkflow, on_delete=models.SET_NULL, null=True)
    created = models.DateTimeField(auto_now_add=True)
    def __str__(self) : 
        return self.title
    
    class Meta:
        db_table = 'sfix_ticket'
