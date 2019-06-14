"""This module is designed to help with transfer the animation profile into correct JSON format"""
# -----------------------------Authorship-----------------------------------------
# -- Authors  : Ella & Yi Ding
# -- Group    : Planning Visualisation
# -- Date     : 2/Oct/2018
# -- Version  : 1.0
# --------------------------------------------------------------------------------
# -----------------------------Reviewer-------------------------------------------
# -- Authors  : Yi Ding
# -- Group    : Planning Visualisation
# -- Date     : 16/Oct/2018
# -- Version  : 1.1
# --------------------------------------------------------------------------------

#######################################################
# Input: A row animation file dictionary
# Output : A complete animation profile dictionary
#######################################################
import re
import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from colour import Color


def transfer(result, objectList):
    """
    This function return the animation file in correct format
    :param result: animation json file
    :param objectList: object list read from the problem pddl file

    :return: correct animation profile
    """
    parse_value(result)
    parse_reference_objects(result, objectList)
    return result


def parse_reference_objects(result, objectList):
    """
    This function replace %name to the objects start with name,%key for key0,key1,key2 etc.
    :param result: animation json file
    :param objectList: object list read from the problem pddl file
    :return: updated animation json file
    """
    for key in result["objects"]["predefine"]:
        raw_list = result["objects"]["predefine"][key]
        newList = []
        for item in raw_list:
            if "%" in item:
                ref_objects = get_ref_objects(item, objectList)
                newList.extend(ref_objects)
            else:
                newList.append(item)

        result["objects"]["predefine"][key] = list(set(newList))


def get_ref_objects(pattern, objectList):
    """
    This function get all the objects from an list which name start with an particular pattern
    :param pattern: name pattern want to search, like key
    :param objectList: object list read from the problem pddl file
    :return: all the objects from objectList which name start with pattern,%key for key0, key1, key2
    """
    pattrn = re.compile("^" + pattern[1:])
    objects = []
    for item in objectList:
        if re.match(pattrn, item):
            objects.append(item)
    return objects


def parse_value(input):
    """
    An recuision function parse all string value to the correct type.Boolean string to boolean,
    interger string to interger,etc
    :param input:
    :return:
    """
    if type(input) is str:
        return transfer_string(input)

    if type(input) is dict:
        for k, v in input.items():
            if type(v) is dict:
                input[k] = parse_value(v)
            elif type(v) is list:
                input[k] = parse_value(v)
            else:
                input[k] = transfer_string(v)
    elif type(input) is list:
        for i, item in enumerate(input):
            input[i] = parse_value(item)
    return input


def transfer_string(value):
    """
    This function turn string in to an correct data type.
    :param value: an value string
    :return: value in the correct data type
    """
    number_pattern = re.compile(r'^[-+]?[0-9]+\.[0-9]+$')

    result = number_pattern.match(value)
    if (result):
        return float(value)
    elif (value.isdigit()):
        return int(value)
    elif (value.lower() == "true"):
        return True
    elif (value.lower() == "false"):
        return False
    elif (value.lower() == "null"):
        return False
    elif (check_color(value)):
        return transfer_color(value)
    else:
        return value


def transfer_color(color):
    """
    This function transfer color name into rgba dictionary
    :param color: string value
    :return: return color dictionary
    """

    c = Color(color).get_rgb()
    rgba = {"r": round(c[0], 4),
            "g": round(c[1], 4),
            "b": round(c[2], 4),
            "a": 1.0
            }

    return rgba


def check_color(color):
    """
    This fucntion check whether a string is color
    :param color: a string
    :return: ture if string represent color, false if not
    """
    try:
        # Converting 'deep sky blue' to 'deepskyblue'
        color = color.replace(" ", "")
        Color(color)
        # if everything goes fine then return True
        return True
    except ValueError:  # The color code was not found
        return False
