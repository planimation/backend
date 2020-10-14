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
import Parser_Functions
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
        try:
            domain_file = request.data['domain'].encode('utf-8').decode('utf-8-sig').lower()
        except Exception as e:
            # for more details error template, could use:
            # return Response({"visualStages": [], "subgoalPool": {}, "subgoalMap": {}, "transferType": 0, "imageTable": {}
            # ,"message": str(e)})
            return Response({"message": "Failed to open domain file \n\n " + str(e)})
        
        try:
            problem_file = request.data['problem'].encode('utf-8').decode('utf-8-sig').lower()
        except Exception as e:
            return Response({"message": "Failed to open problem file \n\n " + str(e)})

        try:
            animation_file = request.data['animation'].encode('utf-8').decode('utf-8-sig')
        except Exception as e:
            return Response({"message": "Failed to open animation file \n\n " + str(e)})

        try:
            domain_file = Parser_Functions.comment_filter(domain_file)
            problem_file = Parser_Functions.comment_filter(problem_file)
            animation_file = Parser_Functions.comment_filter(animation_file)
        except Exception as e:
            return Response({"message": "Failed to filter comments \n\n " + str(e)})

        # add url and parse to get the plan(solution)
        try: 
            if "url" in request.data:
                url_link = request.data['url']
            else:
                url_link = "http://solver.planning.domains/solve"

            if "plan" in request.data:
                actions = request.data['plan'].encode('utf-8').decode('utf-8-sig').lower()
                if "(" in actions and ")" in actions:
                    #TODO: need to raise get_plan_action error 
                    plan = Plan_generator.get_plan_actions(domain_file, actions)
                else:
                    #If user upload the wrong action plan, use the default planner url
                    plan = Plan_generator.get_plan(domain_file, problem_file, url_link)

            else:
                plan = Plan_generator.get_plan(domain_file, problem_file, url_link)
        except Exception as e:
            #Error arise code in in Plan_generator.py line 65 - 70
            return Response({"message": str(e)})
        
        #parse task(domain, problem)
        try:
            predicates_list = Domain_parser.get_domain_json(domain_file)
            problem_dic = Problem_parser.get_problem_dic(problem_file,predicates_list)
            object_list = Problem_parser.get_object_list(problem_file)
        except Exception as e:
            return Response({"message": "Failed to parse the problem \n\n " + str(e)})
        
        #parse animation file
        try:
            animation_profile = json.loads(Animation_parser.get_animation_profile(animation_file,object_list))
        except Exception as e:
            return Response({"message": "Failed to parse the animation file \n\n " + str(e)})

        try:
            stages = Predicates_generator.get_stages(plan, problem_dic, problem_file,predicates_list)
            objects_dic = Initialise.initialise_objects(stages["objects"], animation_profile)
        except Exception as e:
            return Response({"message": "Failed to generate stages \n\n " + str(e)})


        # for testing
        #  myfile = open('plan', 'w')
        #
        # # Write a line to the file
        # myfile.write(json.dumps(plan))
        # # Close the file
        # myfile.close()
        #
        # myfile = open('predicatelist', 'w')
        #
        # # Write a line to the file
        # myfile.write(json.dumps(predicates_list))
        # # Close the file
        # myfile.close()
        #
        # myfile = open('stagejson', 'w')
        #
        # # Write a line to the file
        # myfile.write(json.dumps(stages))
        # # Close the file
        # myfile.close()
        #
        # myfile = open('objects_dic', 'w')
        #
        # # Write a line to the file
        # myfile.write(json.dumps(objects_dic))
        # # Close the file
        # myfile.close()
        # myfile = open('animation_profile', 'w')
        #
        # # Write a line to the file
        # myfile.write(json.dumps(animation_profile))
        # # Close the file
        # myfile.close()

        #Use animation and solution to get visualisation
        try: 
            result = Solver.get_visualisation_dic(stages, animation_profile,plan['result']['plan'],problem_dic)
        except Exception as e:
            return Response({"message": "Failed to solve the animation file \n\n " + str(e)})

        try:
            visualisation_file = Transfer.generate_visualisation_file(result, list(objects_dic.keys()),animation_profile,plan['result']['plan'])
        except Exception as e:
            return Response({"message": "Failed to generate visualisation file \n\n " + str(e)})
        return Response(visualisation_file)

    
class UserGuide(APIView):
    renderer_classes=[TemplateHTMLRenderer]
    template_name = 'UserGuide.html'
    
    def get(self,request):
        return Response({'':""})