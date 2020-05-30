"""This module is responsible to get the planning result from other planning solver"""
#-----------------------------Authorship-----------------------------------------
#-- Authors  : Sai
#-- Group    : Planning Visualisation
#-- Date     : 13/August/2018
#-- Version  : 1.0
#--------------------------------------------------------------------------------
#-----------------------------Reviewer-------------------------------------------
#-- Authors  : Gang chen
#-- Group    : Planning Visualisation
#-- Date     : 23/August/2018
#-- Version  : 1.0
#--------------------------------------------------------------------------------
#-----------------------------Authorship-----------------------------------------
#-- Authors  : Sai
#-- Group    : Planning Visualisation
#-- Date     : 17/Septemeber/2018
#-- Version  : 2.0
#--------------------------------------------------------------------------------
#-----------------------------Reviewer-------------------------------------------
#-- Authors  : Yi Ding
#-- Group    : Planning Visualisation
#-- Date     : 16/Oct/2018
#-- Version  : 2.0
#--------------------------------------------------------------------------------
import urllib.request
import json
import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../' ))
sys.path.append(os.path.dirname(__file__))
import Parser_Functions
from action_plan_parser.parser import Problem
#######################################################
# Input File: A domain file
# Input File: A problem file
# Output : A valid plan will be returned from the planning.domain website
#######################################################

def get_plan(domain_file, problem_file,url):
    """
    This function will send the domain and problem pddl to the solver API to get the plan.
    :param domain_file: domain pddl text
    :param problem_file: problem pddl text
    :param url: Solver url
    :return: plan return by the planning.domain API
    """

    data = {'domain': domain_file,
            'problem': problem_file}

    if url == '':
        url = 'http://solver.planning.domains/solve'
        req = urllib.request.Request(url)
    else:
        req = urllib.request.Request(url)
        
    req.add_header('Content-Type', 'application/json')
    json_data = json.dumps(data)
    json_data_as_bytes = json_data.encode('utf-8')
    req.add_header('Content-Length', len(json_data_as_bytes))
    response = urllib.request.urlopen(req, json_data_as_bytes)
    str_response = response.read().decode('utf-8')
    # use http://solver.planning.domains API to get error info or solution
    plan = json.loads(str_response)
    status = plan['status']
    if status == "error" :
        error = plan['result']['error']
        raise Exception("Failed to get the plan/solution --  " + error)
    else:
        return plan


def get_plan_actions(domain_file, actions):
    domain=Problem(domain_file)
    plan = []
    act_map = {}
    print(actions)
    for a in domain.actions:
        act_map[a.name] = a
    text_blocks = Parser_Functions.get_bracket(actions, 1)
    for act_line in text_blocks:
        print(act_line)
        while ' )' == act_line[-2:]:
            act_line = act_line[:-2] + '  )'
        act_line = act_line.rstrip('\r\n')
        a_name = act_line[1:-1].split(' ')[0]
        if len(act_line.split(' ')) > 1:
            a_params = act_line[1:-1].split(' ')[1:]
        else:
            a_params = False
        a = act_map[a_name]
        plan.append({'name': act_line, 'action': a.export(grounding=a_params)})

    result = {}
    result["result"] = {}
    result["result"]["plan"]=plan
    return result
