from django.contrib import admin
from .models import SfSupportAgent, SfClient,SfWorkflow, SfTicket, SfRagMessage

# Register your models here.
admin.site.register(SfSupportAgent)
admin.site.register(SfClient)
admin.site.register(SfWorkflow)
admin.site.register(SfTicket)
admin.site.register(SfRagMessage)

#http://127.0.0.1:8000/admin
