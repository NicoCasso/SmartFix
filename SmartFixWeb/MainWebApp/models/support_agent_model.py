from django.db import models

class SfSupportAgent(models.Model) :
    name = models.CharField(max_length = 128, default="unknown agent")
    email = models.EmailField(unique=True)
    def __str__(self) : 
        return self.name
    
    class Meta:
        db_table = 'sfix_staff'
    
