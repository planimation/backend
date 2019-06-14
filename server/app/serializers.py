#-----------------------------Authorship-----------------------------------------
#-- Authors  : Gang chen
#-- Group    : Planning Visualisation
#-- Date     : 13/August/2018
#-- Version  : 1.0
#--------------------------------------------------------------------------------
#-----------------------------Reviewer-------------------------------------------
#-- Authors  : Sharukh
#-- Group    : Planning Visualisation
#-- Date     : 27/August/2018
#-- Version  : 1.0
#--------------------------------------------------------------------------------
from rest_framework import serializers
from app.models import PDDL


class PDDLSerializer(serializers.ModelSerializer):
    class Meta:
        model = PDDL
        # fields = '__all__'
        fields = ('id', 'name', 'filetype','file')
