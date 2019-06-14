"""
This file is used for testing the functionality.
The views.py in the parent folder is the main function on the server.


This module intergrate all the other module, it takes the domain PDDL, problem PDDL, and
animation profile, and it write the visualisation file to visualsation.json.

"""
# -----------------------------Authorship-----------------------------------------
# -- Authors  : Sai
# -- Group    : Planning Visualisation
# -- Date     : 13/August/2018
# -- Version  : 1.0
# --------------------------------------------------------------------------------
# -----------------------------Reviewer-------------------------------------------
# -- Authors  : Yi Ding
# -- Group    : Planning Visualisation
# -- Date     : 17/Oct/2018
# -- Version  : 1.0
# --------------------------------------------------------------------------------
import sys
import parser.Plan_generator
import parser.Animation_parser
import parser.Problem_parser
import parser.Predicates_generator
import parser.Domain_parser
import solver.Solver
import solver.Initialise as Initialise
import adapter.visualiser_adapter.Transfer as Transfer
import json


def get_visualisation_file():
    # # This function will call the other modules to generate the visualisaiton file.
    # if len(sys.argv) < 4:
    # 	print("some file is missing, please follow the command below to run the program")
    # 	print("python main.py [dommainfile] [problemfile] [animationprofile]")
    # 	sys.exit()
    try:
	    domain_file = sys.argv[1]
	    problem_file = sys.argv[2]
	    animation_file = sys.argv[3]
	    url_link = sys.argv[4]

        # read animation profile from json
        animation_content = open(animation_file, 'r',encoding='utf-8-sig').read()
        domain_content=open(domain_file, 'r',encoding='utf-8-sig').read().lower()
        problem_content=open(problem_file, 'r',encoding='utf-8-sig').read().lower()
        plan = parser.Plan_generator.get_plan(domain_content,
                                              problem_content,
                                              url_link)

        predicates_list = parser.Domain_parser.get_domain_json(domain_content)

        problem_dic = parser.Problem_parser.get_problem_dic(problem_content, predicates_list)
        object_list = parser.Problem_parser.get_object_list(problem_content)
        animation_profile = json.loads(parser.Animation_parser.get_animation_profile(animation_content, object_list))
        stages = parser.Predicates_generator.get_stages(plan, problem_dic, problem_content,
                                                        predicates_list)

        result = solver.Solver.get_visualisation_dic(stages, animation_profile, plan['result']['plan'], problem_dic)
        # A file called visualistaion.json will be generated in the folder if successful
        objects_dic = Initialise.initialise_objects(stages["objects"], animation_profile)
        final = Transfer.generate_visualisation_file(result, list(objects_dic.keys()), animation_profile,
                                                     plan['result']['plan'])
    except Exception as e:
        message = repr(e)
        final = {"visualStages": [], "subgoalPool": {}, "subgoalMap": {}, "transferType": 0, "imageTable": {},
                 "message": str(message)}


if __name__ == "__main__":
    get_visualisation_file()
