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
#-----------------------------Authorship-----------------------------------------
#-- Authors  : Jian Zhang, Zhichen Lin
#-- Group    : Planimation
#-- Date     : 15/April/2024
#-- Version  : 3.0
#--------------------------------------------------------------------------------

import sys
import os
import time
import requests
from requests.exceptions import ChunkedEncodingError

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../' ))
sys.path.append(os.path.dirname(__file__))
import Parser_Functions
from action_plan_parser.parser import Problem
#######################################################
# Input File: A domain file
# Input File: A problem file
# Output : A valid plan will be returned from the planning.domain website
#######################################################

def get_checkPoint(domain_file, problem_file, url):
    """
    This function will get the URL directory where the planning result will be saved.
    :param domain_file: domain pddl text
    :param problem_file: problem pddl text
    :param url: Solver url
    :return: the URL directory
    """
    data = {'domain': domain_file,
            'problem': problem_file}
    if url == '':
        url = "https://solver.planning.domains:5001/package/dual-bfws-ffparser/solve"
    headers = {
        'Content-Type': 'application/json',
    }
    response = requests.post(url, json=data, headers=headers)
    check_point_resp = response.json()
    if(response.status_code!=200):
        raise Exception("Failed to get the checkpoint --  " + response.text)
    return check_point_resp.get('result')


def get_plan(domain_file, problem_file, url, max_retries=5):
    """
    This function will send the domain and problem pddl to the solver API to get the plan.
    :param domain_file: domain pddl text
    :param problem_file: problem pddl text
    :param url: Solver url
    :param max_retries: maximum number of retries
    :return: plan return by the planning.domain API
    """
    prefix = 'https://solver.planning.domains:5001'
    check_point = get_checkPoint(domain_file, problem_file, url)
    url = prefix + check_point

    adaptor = {"adaptor": "planning_editor_adaptor"}
    headers = {
        'Content-Type': 'application/json'
    }
    retry_count = 0
    wait_time = 2
    while retry_count < max_retries:
        try:
            retry_count += 1
            data = requests.post(url, json=adaptor, headers=headers).json()
            if data.get('status') == 'ok':
                return data.get('plans')[0]
            elif data.get('status') == 'PENDING':
                time.sleep(wait_time)
            else:
                raise ValueError("Unexpected status from the server")
        # To handle to the error raised by Python 3.6 requests package
        except ChunkedEncodingError as e:
            time.sleep(wait_time)
            wait_time += 1
    raise TimeoutError("Maximum retries exceeded while waiting for the plan")


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
