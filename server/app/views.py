from django.shortcuts import render
import sys
import os
import subprocess

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + "vfg/solver"))
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + "vfg/parser"))
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + "vfg/adapter"))
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + "vfg/adapter/visualiser_adapter"))
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + "media_export"))
import Problem_parser  # Step2: parse problem pddl, to get the inital and goal stage
import Predicates_generator  # Step3: manipulate the predicate for each step/stage
import Transfer  # Step4. use the animation profile and stages from step3 to get the visualisation file
import Animation_parser
import Domain_parser
import Parser_Functions
import Solver
import Initialise
import json
import exporter
import Plan_generator
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
from django.http import HttpResponse, HttpResponseNotFound, FileResponse

# (Oct 12, 2020 Changyuan Liu import for download single png)
import re
import shutil


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
            return Response({"message": "Failed to open domain file \n\n " + str(e), "status": 'error'})

        try:
            problem_file = request.data['problem'].encode('utf-8').decode('utf-8-sig').lower()
        except Exception as e:
            return Response({"message": "Failed to open problem file \n\n " + str(e)})

        try:
            animation_file = request.data['animation'].encode('utf-8').decode('utf-8-sig')
        except Exception as e:
            return Response({"message": "Failed to open animation file \n\n " + str(e), "status": 'error'})

        try:
            domain_file = Parser_Functions.comment_filter(domain_file)
            problem_file = Parser_Functions.comment_filter(problem_file)
            animation_file = Parser_Functions.comment_filter(animation_file)
        except Exception as e:
            return Response({"message": "Failed to filter comments \n\n " + str(e), "status": 'error'})

        # add url and parse to get the plan(solution)
        try:
            if "url" in request.data:
                url_link = request.data['url']
            else:
                url_link = "https://solver.planning.domains:5001/package/dual-bfws-ffparser/solve"

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
            # Error arise code in Plan_generator.py line 65 - 70

            return Response({"message": "The process ends with an exception \n\n " + str(e), "status": 'error'})

        # parse task(domain, problem)

        try:
            predicates_list = Domain_parser.get_domain_json(domain_file)
            problem_dic = Problem_parser.get_problem_dic(problem_file, predicates_list)
            object_list = Problem_parser.get_object_list(problem_file)
        except Exception as e:
            return Response({"message": "Failed to parse the problem \n\n " + str(e), "status": 'error'})

        # parse animation file
        try:
            animation_profile = json.loads(Animation_parser.get_animation_profile(animation_file, object_list))
        except Exception as e:
            return Response({"message": "Failed to parse the animation file \n\n " + str(e), "status": 'error'})

        try:
            stages = Predicates_generator.get_stages(plan['result']['plan'], problem_dic, problem_file, predicates_list)
            objects_dic = Initialise.initialise_objects(stages["objects"], animation_profile)
        except Exception as e:
            return Response({"message": "Failed to generate stages \n\n " + str(e), "status": 'error'})

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
            return Response({"message": "Failed to solve the animation file \n\n " + str(e), "status": 'error'})

        try:
            visualisation_file = Transfer.generate_visualisation_file(result, list(objects_dic.keys()),
                                                                      animation_profile,
                                                                      plan['result']['plan'])
            if 'fileType' in request.data:
                output_format = request.data['fileType']
                if output_format != "vfg":
                    vfg = open("vf_out.vfg", "w")
                    vfg.write(json.dumps(visualisation_file))
                    vfg.close()
                    # Process vfg to output files in desired format
                    output_name = capture("vf_out.vfg", output_format)
                    if output_name == "error":
                        response = HttpResponseNotFound("Failed to produce files")
                        return response
                    try:
                        if output_format == "png":
                            output_format = "zip"
                        elif output_format == "lpng" or output_format == "fpng":
                            output_format = "png"
                        response = HttpResponse(open(output_name, 'rb'), content_type='application/' + output_format)
                        response['Content-Disposition'] = 'attachment; filename="' + output_name + '"'
                        delete1 = subprocess.run(["rm", "-rf", output_name])
                        delete2 = subprocess.run(["rm", "-rf", "vf_out.vfg"])
                    except IOError:
                        response = HttpResponseNotFound("File doesn't exist")
                    return response
            return Response(visualisation_file)
        except Exception as e:
            return Response({"message": "Failed to generate visualisation file \n\n " + str(e), "status": 'error'})


class UserGuide(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'UserGuide.html'

    def get(self, request):
        return Response({'': ""})


def zipdir(path, ziph):
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))


# helper function to downlaod single png
def imgdir(path, format):
    for root, dirs, files in os.walk(path):
        if format == "fpng":
            shutil.copy(os.path.join(root, "shot1.png"), "planimation.png")
            return None
        fileLen = len(files)
        for file in files:
            if (int(re.search(r'\d+', file)[0]) == fileLen):
                print(file)
                shutil.copy(os.path.join(root, file), "planimation.png")


# Helper function to capture images and convert to desired format
# Xinzhe Li 22/09/2020

def capture(filename, format, parameters=None):
    # fpng stands for the first png in a sequence and lpng stands for the last
    if format != "gif" and format != "mp4" and format != "png" and format != "webm" and format != "lpng" and format != "fpng":
        return "error"
    p1 = subprocess.run(
        ["sudo", "xvfb-run", "-a", "-s", "-screen 0 640x480x24", "./linux_build/linux_standalone.x86_64", filename,
         "-logfile", "stdlog", "-screen-fullscreen", "0", "-screen-width", "640", "-screen-height", "480"])
    if p1.returncode != 0:
        return "error"
    if format == "png":
        zipf = zipfile.ZipFile("planimation.zip", 'w', zipfile.ZIP_DEFLATED)
        zipdir('ScreenshotFolder', zipf)
        zipf.close()
        # pz = subprocess.run(["zip", "-r", "planimation.zip", "/ScreenshotFolder"])
        format = "zip"
    elif format == "lpng" or format == "fpng":
        imgdir('ScreenshotFolder', format)
        format = "png"
    elif format == "mp4":
        # p2 = subprocess.run(["ffmpeg", "-framerate", "2", "-i", "ScreenshotFolder/shot%d.png", "planimation." + format])
        # p2 = subprocess.run(["ffmpeg", "-framerate", "2", "-i", "ScreenshotFolder/shot%d.png", "-c:v", "libx264", "-vf",
        #                      "fps=25", "-pix_fmt", "yuv420p", "planimation." + format])
        p2 = exporter.export_media(filename, format, parameters)
        if p2 == "error":
            return "error"
        return "planimation.mp4"
    elif format == "gif":
        # p2 = subprocess.run(["ffmpeg", "-framerate", "2", "-i", "ScreenshotFolder/shot%d.png", "planimation." + format])

        p2 = subprocess.run(["ffmpeg", "-framerate", "2", "-i", "ScreenshotFolder/shot%d.png", "-vf",
                             "scale=640:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse",
                             "planimation." + format])

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
    p4 = subprocess.run(["rm", "-rf", "ScreenshotFolder"])
    if p4.returncode != 0:
        return "error"
    return "planimation." + format


class LinkDownloadPlanimation(APIView):
    parser_classes = (MultiPartParser,)

    def post(self, request, format=None):
        try:
            # Parse the request data
            data = json.loads(request.body.decode('utf-8'))
            vfg_data = data["vfg"]
            output_format = data.get("fileType", "")
            parameters = data.get("params", None)

            # Save the vfg data into a file (though ideally this should be handled in memory to avoid I/O overhead)
            with open("vf_out.vfg", "w") as vfg:
                vfg.write(vfg_data)

            output_stream = exporter.export_media("vf_out.vfg", output_format, parameters)

            # Handle the file response
            if output_format == "png":
                content_type = 'application/zip'
                disposition = 'attachment; filename=states.zip'
            else:
                content_type = f'application/{output_format}'
                disposition = f'attachment; filename="planimation.{output_format}"'

            response = FileResponse(output_stream, content_type=content_type)
            response['Content-Disposition'] = disposition

            subprocess.run(["rm", "-rf", "vf_out.vfg"])

            return response

        except Exception as e:
            # Ideally, log the error here for debugging purposes
            return HttpResponseNotFound(str(e))