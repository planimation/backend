#-----------------------------Authorship-----------------------------------------
#-- Authors  : Sai
#-- Group    : Planning Visualisation
#-- Date     : 13/August/2018
#-- Version  : 1.0
#--------------------------------------------------------------------------------
#-----------------------------Reviewer-------------------------------------------
#-- Authors  : Gang
#-- Group    : Planning Visualisation
#-- Date     : 27/August/2018
#-- Version  : 1.0
#--------------------------------------------------------------------------------
from django.db import models

# Create your models here.
class PDDL(models.Model):
    name = models.TextField()
    filetype = models.TextField()
    file = models.FileField(default="")

    class Meta:
        db_table = "PDDL"
