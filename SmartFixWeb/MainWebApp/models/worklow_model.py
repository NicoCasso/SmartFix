from django.db import models
    
class SfWorkflow(models.Model) :
    name= models.CharField(max_length = 128, default="new workflow")
    def __str__(self) : 
        return self.name
    
    class Meta:
        db_table = 'sfix_worklow'