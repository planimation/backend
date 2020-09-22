from django.shortcuts import render
import sys
import os
import subprocess

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + "vfg/solver"))
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + "vfg/parser"))
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + "vfg/adapter"))
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + "vfg/adapter/visualiser_adapter"))
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

# (Sep 22, 2020 Zhaoqi Fang import zipfile for zip pngs and httpResponse)
import zipfile
from django.http import HttpResponse, HttpResponseNotFound


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

        # add url and parse to get the plan(solution)
        try:
            if "url" in request.data:
                url_link = request.data['url']
            else:
                url_link = "http://solver.planning.domains/solve"

            if "plan" in request.data:
                actions = request.data['plan'].encode('utf-8').decode('utf-8-sig').lower()
                if "(" in actions and ")" in actions:
                    # TODO: need to raise get_plan_action error
                    plan = Plan_generator.get_plan_actions(domain_file, actions)
                else:
                    # If user upload the wrong action plan, use the default planner url
                    plan = Plan_generator.get_plan(domain_file, problem_file, url_link)

            else:
                plan = Plan_generator.get_plan(domain_file, problem_file, url_link)
        except Exception as e:
            # Error arise code in in Plan_generator.py line 65 - 70
            return Response({"message": str(e)})

        # parse task(domain, problem)
        try:
            predicates_list = Domain_parser.get_domain_json(domain_file)
            problem_dic = Problem_parser.get_problem_dic(problem_file, predicates_list)
            object_list = Problem_parser.get_object_list(problem_file)
        except Exception as e:
            return Response({"message": "Failed to parse the problem \n\n " + str(e)})

        # parse animation file
        try:
            animation_profile = json.loads(Animation_parser.get_animation_profile(animation_file, object_list))
        except Exception as e:
            return Response({"message": "Failed to parse the animation file \n\n " + str(e)})

        stages = Predicates_generator.get_stages(plan, problem_dic, problem_file, predicates_list)
        objects_dic = Initialise.initialise_objects(stages["objects"], animation_profile)

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

        # Use animation and solution to get visualisation
        try:
            result = Solver.get_visualisation_dic(stages, animation_profile, plan['result']['plan'], problem_dic)
        except Exception as e:
            return Response({"message": "Failed to solve the animation file \n\n " + str(e)})

        visualisation_file = Transfer.generate_visualisation_file(result, list(objects_dic.keys()), animation_profile,
                                                                  plan['result']['plan'])
        return Response(visualisation_file)


class UserGuide(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'UserGuide.html'

    def get(self, request):
        return Response({'': ""})


def zipdir(path, ziph):
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))


# Helper function to capture images and convert to desired format
# Xinzhe Li 22/09/2020
def capture(filename, format):
    if format != "gif" and format != "mp4" and format != "png" and format != "webm":
        return "error"
    p1 = subprocess.run(["sudo", "./linux_standalone.x86_64", filename, "-batchmode", "-logfile", "stdlog"])
    if p1.returncode != 0:
        return "error"
    subprocess.run(["chmod", ""])
    if format == "png":
        zipf = zipfile.ZipFile("planimation.zip", 'w', zipfile.ZIP_DEFLATED)
        zipdir('ScreenshotFolder', zipf)
        zipf.close()
        format = "zip"
    elif (format == "mp4") or (format == "gif"):
        p2 = subprocess.run(["ffmpeg", "-framerate", "2", "-i", "ScreenshotFolder/shot%d.png", "planimation." + format])
        if p2.returncode != 0:
            return "error"
    else:
        p2 = subprocess.run(["ffmpeg", "-framerate", "2", "-i", "ScreenshotFolder/shot%d.png",
                             "ScreenshotFolder/buffer.mp4"])
        if p2.returncode != 0:
            return "error"
        p3 = subprocess.run(["ffmpeg", "-i", "ScreenshotFolder/buffer.mp4", "planimation.webm"])
        if p3.returncode != 0:
            return "error"
    """
    p4 = subprocess.run(["rm", "-rf", "ScreenshotFolder"])
    if p4.returncode != 0:
        return "error"
    """
    return "planimation." + format


class LinkDownloadPlanimation(APIView):
    parser_classes = (MultiPartParser,)

    """
    def zipdir(self, path, ziph):
        for root, dirs, files in os.walk(path):
            for file in files:
                ziph.write(os.path.join(root, file))
    """

    def post(self, request, format=None):
        try:
            vfg_file = request.data['vfg'].encode('utf-8').decode('utf-8-sig').lower()
            # print(vfg_file)
        except Exception as e:
            return Response({"message": "Failed to open vfg file \n\n " + str(e)})

        try:
            fileType = request.data['fileType']
            # print(fileType)
        except Exception as e:
            return Response({"message": str(e)})

        # Save vfg file in order to use standalone for passing vfg
        vfg = open("vf_out.vfg", "w")
        vfg.write(vfg_file)
        vfg.close()

        # Process vfg to output files in desired format
        output_name = capture("vf_out.vfg", fileType)
        if output_name == "error":
            response = HttpResponseNotFound("Failed to produce files")
            return response
        try:
            if fileType == "png":
                fileType = "zip"
            response = HttpResponse(open(output_name, 'rb'), content_type='application/'+fileType)
            response['Content-Disposition'] = 'attachment; filename="'+output_name+'"'
            # delete = subprocess.run(["rm", "-rf", output_name])
        except IOError:
            response = HttpResponseNotFound('File not exist')
        return response
