"""This module is designed to help with parse animation pddl into a valid animation
profile in JSON format"""
# -----------------------------Authorship-----------------------------------------
# -- Authors  : Gang
# -- Group    : Planning Visualisation
# -- Date     : 10/Sep/2018
# -- Version  : 1.0
# --------------------------------------------------------------------------------
# -----------------------------Reviewer-------------------------------------------
# -- Authors  : Yi Ding
# -- Group    : Planning Visualisation
# -- Date     : 16/Oct/2018
# -- Version  : 1.0
# --------------------------------------------------------------------------------
import re
import sys
import json
import copy
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../' + "adapter/ap_adapter"))
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../' + "extension"))
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../' + "parser"))
import Custom_functions
import Adapter
import Parser_Functions


#######################################################
# Input File: A animation PDDF file
# Output : A complete animation profile in JSON format
#######################################################

def get_animation_profile(animation_pddl, object_list):
    text_to_parse = animation_pddl
    # text_to_parse = animation_pddl.lower()

    # Final result structure that is going to be returned
    result = {"objects": {"default": {},
                          "predefine": {},
                          "custom": {}},
              "predicates_rules": {},
              "visual": {},
              "imageTable": {"m_keys": [],
                             "m_values": []}}
    parse(copy.copy(text_to_parse), result)
    Adapter.transfer(result, object_list)
    return json.dumps(result)


def parse(text, result):
    """
    :param text: whole text file
    :param result: animation dictionary
    :return: updated animation dictionary
    """
    text_blocks = Parser_Functions.get_bracket(text, 2)
    for text_block in text_blocks:
        if "visual" in text_block:
            parse_visual(text_block, result)
        elif "predicate" in text_block:
            parse_predicate(text_block, result)
        elif "image" in text_block:
            parse_image(text_block, result)


def parse_visual(text_to_parse, result):
    """
    This function is used to parse visual block in animation pddl
    :param text_to_parse: text contain one visual text block
    :param result: animation dictionary
    :return: updated animation dictionary
    """
    # --------------------------------------------
    # Patterns that are going to be used for Visual
    pattern_visual = ":visual"
    pattern_type = ":type"
    pattern_objects = ":objects"
    pattern_properties = ":properties"

    # Get the value of the visual
    temp_visual_block = text_to_parse[text_to_parse.index(pattern_visual):]
    temp_visual_block = Parser_Functions.get_one_block(temp_visual_block)

    temp_visual_pattern = re.compile("(?i)" + pattern_visual + "\s[\w\-]+", re.IGNORECASE)
    temp_subshape, temp_subshape_value = temp_visual_pattern.findall(temp_visual_block)[0].split()

    sublist = {}

    # Get the value of type
    temp_regex_pattern = re.compile(pattern_type + "\s[\w\-]+", re.IGNORECASE)
    temp_subelement, temp_subelement_value = temp_regex_pattern.search(temp_visual_block)[0].split()

    if "objects" in temp_visual_block:
        objects_list = parseObjectLine(pattern_objects, temp_visual_block)
        result["objects"][temp_subelement_value][temp_subshape_value] = objects_list
    elif (temp_subelement_value == "default"):
        result["objects"][temp_subelement_value] = temp_subshape_value

    # Get the value of properties
    temp_property_block = temp_visual_block[temp_visual_block.index(pattern_properties) + len(pattern_properties):]
    temp_property_block = Parser_Functions.get_one_block(temp_property_block)
    temp_properties_pattern = re.compile("\([a-zA-Z0-9_.-]*\s[#a-zA-Z0-9_.-]*\)")
    temp_properties = temp_properties_pattern.findall(temp_property_block)
    for x in temp_properties:
        x, y = x.replace('(', '').replace(')', '').split()
        sublist[x] = y
    result["visual"][temp_subshape_value] = sublist
    return result;


def parseObjectLine(pattern, text):
    """
    :param pattern: line start with an pattern
    :param text: one line of text
    :return: an array of objects
    """
    temp_objects_pattern = re.compile(pattern + "\s*(\([^\)]+\)|[\w\-\%]+)", re.IGNORECASE)
    try:
        objectsStr = temp_objects_pattern.search(text).group(1)
    except:
        return []
    if "(" in objectsStr:
        return Parser_Functions.parse_objects(objectsStr)
    else:
        return [objectsStr]


def parse_predicate(text_to_parse, result):
    """
    This function is used to parse predicate text block
    :param text_to_parse: test contain one predicate text block
    :param result: animation profile dictionary
    :return:
    """
    pattern_predicate = ":predicate"
    pattern_parameters = ":parameters"
    pattern_custom = ":custom"
    pattern_priority = ":priority"
    pattern_effect = ":effect"
    # Get the value of the predicate

    temp_visual_block = text_to_parse[text_to_parse.index(pattern_predicate):]
    temp_visual_block = Parser_Functions.get_one_block(temp_visual_block)

    temp_visual_pattern = re.compile(pattern_predicate + "\s[\w\-]+", re.IGNORECASE)
    temp_subshape, temp_subshape_value = temp_visual_pattern.findall(temp_visual_block)[0].split()

    if "priority" in temp_visual_block:
        priority_pattern = re.compile(pattern_priority + "\s*(\(\d+\)|[\d]+)", re.IGNORECASE)
        priority = priority_pattern.findall(temp_visual_block)

    # Get the value of parameters
    temp_regex_pattern = re.compile(pattern_parameters + " " + "\((.*?)\)", re.IGNORECASE)
    objectList = temp_regex_pattern.findall(temp_visual_block)[0].split()

    customObjectList = parseObjectLine(pattern_custom, temp_visual_block)
    # Get the value of effect
    temp_effect_block = temp_visual_block[temp_visual_block.index(pattern_effect) + len(pattern_effect):]
    temp_effect_block = Parser_Functions.get_one_block(temp_effect_block)
    require_dic = {}
    result["predicates_rules"][temp_subshape_value] = parse_rules(temp_effect_block, require_dic)
    result["predicates_rules"][temp_subshape_value]["require"] = require_dic
    result["predicates_rules"][temp_subshape_value]["objects"] = objectList
    if "priority" in temp_visual_block:
        result["predicates_rules"][temp_subshape_value]["priority"] = priority[0]
    if len(customObjectList) > 0:
        result["predicates_rules"][temp_subshape_value]["custom_obj"] = customObjectList


def parse_image(text_to_parse, result):
    """
    This function is used to parse Image text block
    :param text_to_parse: text contain one image text block
    :param result: animation profile dictionary
    :return:
    """
    pattern_image = ":image"
    temp_image_block = text_to_parse[text_to_parse.index(pattern_image):]
    temp_image_block = Parser_Functions.get_one_block(temp_image_block)
    patternPare = re.compile(r'\((.*?)\)')
    imagePareList = patternPare.findall(temp_image_block)
    for imagePare in imagePareList:
        name, value = imagePare.split()
        result["imageTable"]["m_keys"].append(name)
        result["imageTable"]["m_values"].append(value)





def parse_rule(rule, require_dic):
    """
    This function is used to parse one particular animation rule
    :param rule: text contain one rule
    :param require_dic: an dictionary which will record the required objects and its parameters to
                        apply this rule
    :return: an rule in dictionary format
    """
    template = {
        "left": {},
        "value": {}
    }
    rulePattern = re.compile(r'\((\w+)\s+(\([^)]+\))\s*(\(.*\)|[\d\w#-]+)\)')
    divide_rule = re.search(rulePattern, rule)
    rule_type = divide_rule.group(1)
    left_object = divide_rule.group(2)
    right_value = divide_rule.group(3)
    middle = Parser_Functions.parse_objects(left_object)
    template["left"][middle[0]] = middle[1:]
    if "function" in rule:
        template["value"] = parse_function(right_value, require_dic)
    elif "(" not in right_value:
        value_pattern = re.compile(r'\(equal\s+\([^)]+\)\s*([\d\w#-]+)\)')
        searchValue = re.search(value_pattern, rule)
        value = searchValue.group(1)
        template["value"]["equal"] = value
    elif "add" in right_value:
        template["value"] = parse_add(right_value, require_dic)
    elif "(" in right_value:
        name, value = Parser_Functions.parse_objects(right_value)
        template["value"]["equal"] = {name: value}
        update_require(require_dic, name, value)
    return template

def parse_function(text, require_dic):
    """
    This function is used to parse function text block into dictionary format
    :param text: text contain function text block
    :param require_dic: an dictionary which will record the required objects and its parameters to
                        run the function
    :return: a function dictionary
    """
    template = {
        "fname": "",
        "obj_indexs": [],
        "settings": {
        }
    }

    name_pattern = re.compile(r'\(function\s*(\w+)\s*\(.*')
    searchName = re.search(name_pattern, text)
    name = searchName.group(1)
    template["fname"] = name
    # (objects a b c)
    objects_pattern = re.compile(r'\(objects\s+([^)]+)\)')
    searchObj = re.search(objects_pattern, text)
    objects = re.split(r'\s+', searchObj.group(1))
    template["obj_indexs"] = objects
    require = Custom_functions.customf_controller(name, None, None, None, None, True)["require"]
    for key, value in require.items():
        index = int(key)
        for item in value:
            obj_name = objects[index]
            update_require(require_dic, obj_name, item)
    if "settings" in text:
        settings_pattern = re.compile(r'\(settings\s+(\s*\([^)]*\)\s*)+\)')
        searchSetting = re.search(settings_pattern, text)
        SettingStr = searchSetting.group(0)
        settingList = Parser_Functions.get_bracket(SettingStr, 2)
        for setting in settingList:
            sname, svalue = Parser_Functions.parse_objects(setting)
            template["settings"][sname] = svalue

    return {"function": template}


def parse_add(text, require_dic):
    """
    This function parse the add text block into dictionary format
    :param text: text contain one add text block
    :param require_dic: an dictionary which will record the required objects and its parameters to
                        do the addition
    :return: a dictionary contain add information
    """
    template = {
        "add": []
    }
    reference = Parser_Functions.get_bracket(text, 2)
    if reference:
        for item in reference:
            name, value = Parser_Functions.parse_objects(item)
            template["add"].append({name: value})
            update_require(require_dic, name, value)
    digital_pattern = re.compile(r'[-\d]+')
    digital_list = re.findall(digital_pattern, text)
    if digital_list:
        for item in digital_list:
            template["add"].append(int(item))
    return template


def update_require(require_dic, name, value):
    """
    :param require_dic: a dictionary contain all the require objects and its properties to solve a
            predicate. For example, on(a,b) is an predicate and it require b's x and y.
    :param name: object name
    :param value: object property
    """
    if name not in require_dic:
        require_dic[name] = []
    require_dic[name].append(value)


def parse_actionrule(rule, require_dic):
    """
    This function is used to parse action rule, action rule is used to create new object to
    show in visualiser. Such as "line" for (connect node1-1 node1-2)
    :param rule: text contain one rule
    :param require_dic: a dictionary contain all the require objects and its properties to solve a
            predicate.
    :return: action rule in dictionary format
    """
    template = {
        "action": {}
    }
    rulePattern = re.compile(r'\((\w+)\s*(\(.*\))\)')
    divide_rule = re.search(rulePattern, rule)
    rule_type = divide_rule.group(1)
    right_value = divide_rule.group(2)

    if "function" in rule:
        template["action"] = parse_function(right_value, require_dic)
    return template


def parse_rules(text, require_dic):
    """
    This function is used to parse all the predicate rules in the effect part of predicate text block
    :param text: text contain several rules
    :param require_dic: a dictionary contain all the require objects and its properties to solve a
            predicate.
    :return: a dictionary contain all the rules
    """
    template = {
        "rules": []
    }
    rules = Parser_Functions.get_bracket(text, 2)
    for i, rule in enumerate(rules):
        newrule = "rule" + str(i + 1)
        template["rules"].append(newrule)
        if "equal" in rule or "assign" in rule:
            template[newrule] = parse_rule(rule, require_dic)
        elif "action" in rule:
            template[newrule] = parse_actionrule(rule, require_dic)
    return template
