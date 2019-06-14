from django.shortcuts import render
import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' +"vfg/solver"))
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' +"vfg/parser"))
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' +"vfg/adapter"))
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' +"vfg/adapter/visualiser_adapter"))
import Plan_generator  # Step1: get plan from planning domain api
import Problem_parser  # Step2: parse problem pddl, to get the inital and goal stage
import Predicates_generator  # Step3: manipulate the predicate for each step/stage
import Transfer  # Step4. use the animation profile and stages from step3 to get the visualisation file
import Animation_parser
import Domain_parser
import Solver
import Initialise
import json
# Create your views here.

from app.models import PDDL
from app.serializers import PDDLSerializer

from rest_framework import viewsets
from rest_framework.parsers import BaseParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.renderers import TemplateHTMLRenderer

# Create your views here.
class PDDLViewSet(viewsets.ModelViewSet):
    queryset = PDDL.objects.all()
    serializer_class = PDDLSerializer
    
class PlainTextParser(BaseParser):
    """
    Plain text parser.
    """
    media_type = 'text/plain'

    def parse(self, stream, media_type="text/plain", parser_context=None):
        """
        Simply return a string representing the body of the request.
        """
        return stream.read()
    
class LinkUploadView(APIView):
    parser_classes = (MultiPartParser,)

    def post(self, request, filename, format=None):

        # .encode('utf-8').decode('utf-8-sig') will remove the \ufeff in the string when add string as value in
        # a dictionary.
        domain_file = request.data['domain'].encode('utf-8').decode('utf-8-sig').lower()
        problem_file = request.data['problem'].encode('utf-8').decode('utf-8-sig').lower()
        animation_file = request.data['animation'].encode('utf-8').decode('utf-8-sig')

        # add url
        if "url" in request.data:
            url_link = request.data['url']
        else:
            url_link = "http://solver.planning.domains/solve"

        predicates_list = Domain_parser.get_domain_json(domain_file)
        plan = Plan_generator.get_plan(domain_file, problem_file, url_link)
        problem_dic = Problem_parser.get_problem_dic(problem_file,predicates_list)

        object_list = Problem_parser.get_object_list(problem_file)
        animation_profile = json.loads(Animation_parser.get_animation_profile(animation_file,object_list))
        stages = Predicates_generator.get_stages(plan, problem_dic, problem_file,predicates_list)
        objects_dic = Initialise.initialise_objects(stages["objects"], animation_profile)

        myfile = open('stagejson', 'w')

        # Write a line to the file
        myfile.write(json.dumps(stages))
        # Close the file
        myfile.close()

        myfile = open('objects_dic', 'w')

        # Write a line to the file
        myfile.write(json.dumps(objects_dic))
        # Close the file
        myfile.close()
        myfile = open('animation_profile', 'w')

        # Write a line to the file
        myfile.write(json.dumps(animation_profile))
        # Close the file
        myfile.close()


        result = Solver.get_visualisation_dic(stages, animation_profile,plan['result']['plan'],problem_dic)

        visualisation_file = Transfer.generate_visualisation_file(result, list(objects_dic.keys()),animation_profile,plan['result']['plan'])


        return Response(visualisation_file)

    
class UserGuide(APIView):
    renderer_classes=[TemplateHTMLRenderer]
    template_name = 'UserGuide.html'
    
    def get(self,request):
        return Response({'':""})