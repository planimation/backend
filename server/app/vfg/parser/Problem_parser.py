"""This module is designed to help with getting a list of predicates for INIT and GOAL states"""

# -----------------------------Authorship-----------------------------------------
# -- Authors  : Gang CHEN
# -- Group    : Planning Visualisation
# -- Date     : 13/August/2018
# -- Version  : 1.0
# --------------------------------------------------------------------------------
# -----------------------------Reviewer-------------------------------------------
# -- Authors  : Sharukh
# -- Group    : Planning Visualisation
# -- Date     : 23/August/2018
# -- Version  : 1.0
# --------------------------------------------------------------------------------
# -----------------------------Authorship-----------------------------------------
# -- Authors  : Sunmuyu Zhang
# -- Group    : Planning Visualisation
# -- Date     : 07/Septemeber/2018
# -- Version  : 2.0
# --------------------------------------------------------------------------------
# -----------------------------Reviewer-------------------------------------------
# -- Authors  : Sai
# -- Group    : Planning Visualisation
# -- Date     : 09/Septemeber/2018
# -- Version  : 2.0
# --------------------------------------------------------------------------------
import re
import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../' + "parser"))
import Parser_Functions


def get_problem_dic(problem_text, predicates_lists):
    """
    The function will parse the problem pddl and get the Initial predicates and
    and goal predicates
    :param problem_text: problem pddl text
    :param predicates_lists: all the available predicate from domain pddl
    :return: a dictionary contains INIT and GOAL states(predicates).
    """

    # Prepare REGEX for each predicate
    try:
        get_regex_list(predicates_lists)
    except:
        raise ValueError("Empty predicates found")

    text_blocks = Parser_Functions.get_bracket(problem_text, 2)

    result = []
    for block in text_blocks:
        if "init" in block:
            init_object_list = get_state_list(predicates_lists, block)
            result.append({"init": init_object_list})
        elif "goal" in block:
            goal_object_list = get_state_list(predicates_lists, block)
            result.append({"goal": goal_object_list, "goal-condition": ["and"]})

    return result


def get_regex_list(predicates_lists):
    """
    This function used to make an predicate regular expression pattern
    :param predicates_lists: a dictionary contain predicate name and the number of objects pair
    :return: dictionary which contain predicate name and predicate pattern pair
    """
    for k, v in predicates_lists.items():

        regular_expression = k.replace(" ", "")
        for x in range(v):
            regular_expression += "\s[\w\-]+"
        predicates_lists[k] = regular_expression


def get_state_list(predicates_pattern_dic, text_block):
    """
    This function turn all the predicate in text block into dictionary format
    :param predicates_pattern_dic: dictionary which contain predicate name and predicate pattern pair
    :param text_block: a text block contain list of predicates in plain text format
    :return: return predicate list in dictionary format
    """
    result = []

    for predicate_name, predicate_pattern in predicates_pattern_dic.items():
        temp_pattern = re.compile("\(" + predicate_pattern)
        predicates = temp_pattern.findall(text_block)
        if predicates:
            number_of_objects = len(predicates[0].split()) - 1

            for predicate in predicates:
                data_object = {"name": predicate_name.replace(" ", ""), "objectNames": []}
                if (number_of_objects > 0):
                    data_object["objectNames"].extend(predicate.split()[1:])
                else:
                    data_object["objectNames"] = ["No objects"]
                result.append(data_object)
    return result


def get_separate_state_list(predicates_pattern_dic, text_block):
    """
    This function turn all the predicate in text block into dictionary format 
    and separate them into two list according to their predicate params
    :param predicates_pattern_dic: dictionary which contain predicate name and predicate pattern pair
    :param text_block: a text block contain list of predicates in plain text format
    :return add_result: predicate lists in dictionary format that will be added
    :return remove_result: predicate lists in dictionary format that will be removed
    """
    add_result = []
    remove_result = []

    for predicate_name, predicate_pattern in predicates_pattern_dic.items():
        pattern = "((not\\s+)?\\(" + predicate_pattern + ")"
        temp_pattern = re.compile(pattern)
        predicates = temp_pattern.findall(text_block)
        if predicates:
            for predicate in predicates:
                if predicate[1]:
                    negated = False
                    predicate = re.sub(r"not\s+", "", predicate[0])
                else:
                    negated = True
                    predicate = predicate[0]

                data_object = {"name": predicate_name.replace(" ", ""), "objectNames": []}
                if len(predicate.split()) > 1:
                    data_object["objectNames"].extend(predicate.split()[1:])
                else:
                    data_object["objectNames"] = ["No objects"]
                if negated:
                    add_result.append(data_object)
                else:
                    remove_result.append(data_object)
    return add_result, remove_result


def get_object_list(problem_text):
    """
    This function return the object list in problem PDDL
    :param problem_text: problem text
    :return: object list
    """
    block_list = Parser_Functions.get_bracket(problem_text, 2)
    for block in block_list:
        if "objects" in block:
            objects = Parser_Functions.parse_objects(block)
            return objects
