"""This module will compute the visulisation file by using the stages predicates and animation"""
# -----------------------------Authorship-----------------------------------------
# -- Authors  : YD
# -- Group    : Planning Visualisation
# -- Date     : 16/September/2018
# -- Version  : 2.0
# --------------------------------------------------------------------------------
# -----------------------------Reviewer-------------------------------------------
# -- Authors  : Sai
# -- Group    : Planning Visualisation
# -- Date     : 16/October/2018
# -- Version  : 2.0
# --------------------------------------------------------------------------------
import copy
import os
import sys
import re

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../' + "extension"))
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + "vfg/solver"))
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import Custom_functions
import Initialise
import Subgoal


def check_rule_complete(predicate, objects_dic, predicates_rules):
    """
    This funtion will check whether the predicate can be solved.
    It will check all the referenced object value by using the predicates_rules,
    for example, (on a b) as an predicates, the animation rules will say to define
    the position of a, it must know b's x postion and y position first. If b's refereced
    value has not been defined, the check_rule_complete function will return false.

    :param predicate: a predicate that need to be checked, eg.(on-table b).
    :param objects_dic: the current objects dictionary that need to be solved.
    :param predicates_rules: rules defined the animation rule for the predicates.
    :return:  True: if the predicate can be solved.
              False: if the predicate can not be solved.
    """

    pname = predicate["name"]
    predicate_rule = predicates_rules[pname]
    objects_list_ref = predicate_rule["objects"]
    objects = predicate["objectNames"]
    if "custom_obj" in predicate_rule:
        # addtional custom object not in the real pddl file
        custom_obj = predicate_rule["custom_obj"]
        # complete object list
        object_list = objects + custom_obj
        objects_list_ref = objects_list_ref + custom_obj
    else:
        object_list = objects
    obj_ref_dic = dict(zip(objects_list_ref, object_list))
    if "require" in predicate_rule:
        for obj_index in predicate_rule["require"]:
            right_args = predicate_rule["require"][obj_index] 
            if(len(right_args) == 0) : property = ""
            elif(len(right_args) >=1) : property = right_args[0]
            if (obj_index not in obj_ref_dic):                  # raise error when object doesn't exist
                raise Exception("%s used in (%s, %s) doesn't exsits as an argument of predicate %s"
             %(obj_index,obj_index, property, pname.upper()))
            for property in predicate_rule["require"][obj_index]:
                objectname = obj_ref_dic[obj_index]         
                if (property not in objects_dic[objectname]):   # raise error when object doesn't exist
                    constructString = "(%s, %s)" %(obj_index, property)
                    raise Exception ("'%s' used in %s doesn't exist as an argument in predicate %s" 
                %(property, constructString, pname.upper()))
                if objects_dic[objectname][property] is False:
                    return False
    return True


def applypredicates(predicate,
                    objects_dic,
                    predicates_rules,
                    gstate):
    """
    update the value of realated obj in the objects_dic by applying the animation rules.
    For example, (on-table a) will set the a's x value by using distributex function and a's
    y value to 0.
    :param predicate:a predicate that need to be solved.
    :param objects_dic: a objects dictionary that contain all the objects and its attributes.
    :param predicates_rules:rules defined the animation rule for the predicates
    :param gstate: an dictionary which remember all the state for custom function
    :return:
    """

    pname = predicate["name"]
    predicate_rule = predicates_rules[pname]
    objects_list_ref = predicate_rule["objects"]
    # objects in the real pddl file
    objects = copy.deepcopy(predicate["objectNames"])
    if "custom_obj" in predicate_rule:
        # addtional custom object not in the real pddl file
        custom_obj = predicate_rule["custom_obj"]
        # complete object list
        object_list = objects + custom_obj
        objects_list_ref = objects_list_ref + custom_obj
    else:
        object_list = objects

    obj_ref_dic = dict(zip(objects_list_ref, object_list))
    for rulename in predicate_rule["rules"]:
        if "value" in predicate_rule[rulename]:
            rule = predicate_rule[rulename]

            #raise error when the object is not defined
            try:
                object_index, left, propertyname = get_objname_property(rule["left"], obj_ref_dic)
            except Exception as e:
                (object_index, right_args) = list(rule["left"].items())[0]
                if(len(right_args) == 0) : property = ""
                elif(len(right_args) >=1) : property = right_args[0]
                raise Exception("%s used in (%s, %s) doesn't exsit as an argument of predicate %s" 
            %(object_index, object_index, property, pname.upper()))

            # raise error when property is not given correctly
            if (propertyname == []):                                     # when property or is not given
                construct = "(%s, )" %object_index
                raise Exception ("%s used at predicate %s needs more arguments" %(construct, pname.upper()))
            elif (propertyname[0] not in objects_dic[left]):             # when a wrong proterty is given
                construct = "(%s, %s)" %(object_index,propertyname[0])
                raise Exception ("'%s' used in %s doesn't exist as a property of %s at predicate %s" 
            %(propertyname[0],construct, object_index, pname.upper()))
            
            value = predicate_rule[rulename]["value"]
            if "function" in value:
                fproperty = value["function"]
                fname = fproperty["fname"]
                obj_indexs = fproperty["obj_indexs"]
                if "settings" in fproperty:
                    settings = fproperty["settings"]
                else:
                    settings = {}
                state = gstate[fname]
                obj_list = []
                for obj_index in obj_indexs:
                    objname = obj_ref_dic[obj_index]
                    obj_list.append({objname: objects_dic[objname]})
                result = Custom_functions.customf_controller(fname, obj_list, settings, state, False)
                update_object(objects_dic[left], propertyname, gstate, fname, result)
            elif "equal" in value:
                right_value = value["equal"]
                if type(right_value) is not dict:
                    objects_dic[left][propertyname[0]] = right_value
                else:
                    if "r" in right_value:  # for color
                        objects_dic[left][propertyname[0]] = right_value
                    else:
                        object_index, right_object, right_property = get_objname_property(right_value, obj_ref_dic)
                        objects_dic[left][propertyname[0]] = objects_dic[right_object][right_property]

            elif "add" in value:
                rightvalue = 0
                for additem in value["add"]:
                    if type(additem) is dict:
                        r_obj_index, right_object, right_property = get_objname_property(additem, obj_ref_dic)
                        addvalue = objects_dic[right_object][right_property]
                        rightvalue += addvalue
                    else:
                        rightvalue += additem
                objects_dic[left][propertyname[0]] = rightvalue
        else:
            # if the rule is action rule
            action = predicate_rule[rulename]["action"]
            if "function" in action:
                fproperty = action["function"]
                fname = fproperty["fname"]
                obj_indexs = fproperty["obj_indexs"]
                if "settings" in fproperty:
                    settings = fproperty["settings"]
                else:
                    settings = {}
                state = gstate[fname]
                obj_list = []
                for obj_index in obj_indexs:
                    objname = obj_ref_dic[obj_index]
                    obj_list.append({objname: objects_dic[objname]})

                key, value = Custom_functions.customf_controller(fname, obj_list, settings, state, False)
                objects_dic[key] = value


def get_objname_property(property_dic, obj_ref_dic):
    """
    This function turn the general object and property dic into a specific object and property tuple.
    :param property_dic: dictionary contain the key and it's property. eg. {"?x",["x"]}
    :param obj_ref_dic: dictionary contain the key and it's corresponding object. eg. {"?x","obj"}
    :return: a tuple which conatin the object name and it's properties ("obj","x")
    """

    object_index, propertyname = list(property_dic.items())[0]
    objname = obj_ref_dic[object_index]
    return object_index, objname, propertyname


def update_object(objectdic, properties, gstate, fname, result):
    """
    This function update object dic based on the custom function result
    :param objectdic: an single object dictionary that need to be solved
    :param properties: properties of the object need to be updated
    :param gstate: state of all the custom function
    :param fname: function name
    :param result: custom function result

    """
    new_properties, newstate = result
    gstate[fname] = newstate
    if len(properties) != len(new_properties):
        raise ValueError("customer function: " + fname + " returns " + str(len(new_properties)) + " properties, but "
                         + str(len(properties)) + " properties was given.")
    try:
        for property in properties:
            objectdic[property] = new_properties[property]
    except:
        helpinfo = "("
        for key in new_properties.keys():
            helpinfo += str(key) + " "
        helpinfo += ")"
        raise ValueError("Property " + str(property) + " is not returned by customer function:" + fname +
                         ", property " + helpinfo + " are returned")


def solvepredicates(predicates, objects_dic, predicates_rules, gstate):
    """
    This function will pop an predicate from a list of predicates, and try to solve
    it, the predicate will be put back to the predicates list if it can not be solved at
    one turn. The funtion will return true if all the predicates has been solved.
    :param predicates: a list of predicates that need to be solved.
    :param objects_dic: a dictionary of objects that its attribtes has to be solved
    :param predicates_rules: animation rules of predicates.
    :param gstate: global state of all custom function
    :return: True if the predicate are solved
    """
    """This function will pop an predicate from a list of predicates, and try to solve
    it, the predicate will be put back to the predicates list if it can not be solved at
    one turn. The funtion will return true if all the predicates has been solved.
    Args:
        predicates(list of String): a list of predicates that need to be solved.
        objects_dic(dictionary): a dictionary of objects that its attribtes has to be solved
        predicates_rules(dictonaru): animation rules of predictates.
        space(array):an array that will be used for distributex funtion, it remeber the current obj
              that in the space.

    """
    i = 0
    while (predicates and i < 2000):
        predicate = predicates.pop(0)
        if predicate["name"] not in predicates_rules:
            continue
        if check_rule_complete(predicate, objects_dic, predicates_rules):

            applypredicates(predicate, objects_dic, predicates_rules, gstate)
        else:
            if not predicates:  # if the last predicate can not be solved
                return False
            predicates.append(predicate)
        i += 1
    return True


def keysort(predicate_name, predicates_rules):
    """
    This funtion will return weight for each predicates, default 10(not important).
    0 means very important.
    :param predicate_name: name of a predicate
    :param predicates_rules: predicate_rules for the all predicate
    :return: integer
    """
    if predicate_name in predicates_rules:
        if "priority" in predicates_rules[predicate_name]:
            return predicates_rules[predicate_name]["priority"]
        else:
            return 10
    else:
        return 10


def priority(predicates, predicates_rules):
    """
    This funtion will return sorted predicates based on the priority point
    :param predicates: list of predicate
    :param predicates_rules: predicate_rules for the all predicate
    :return: sorted predicates list
    """
    return sorted(predicates, key=lambda k: keysort(k["name"], predicates_rules))


def solve_all_stages(stages, objects_dic, predicates_rules, gstate, actionlist, problem_dic):
    """
    This funtion will run through each stage which contains a list of predicates, solve the
    predictaes and get the solved visualistaion file.
    :param stages: a dictinonary which contain list of predicates for different stages/steps.
    :param objects_dic: a dictionary of objects which need to be solved.
    :param predicates_rules: animation rules for the predicates
    :param gstate(global state): a dictionary contain all the custom function state information
    :param actionlist: action list
    :param problem_dic: problem dictionary contain the goal state
    :return: visualisation dictionary that contain the location of each object for different stages
    """

    result = {}
    result["visualStages"] = []
    for stage in stages:

        stage_dic = {}
        object_dic_copy = copy.deepcopy(objects_dic)
        predicates = stage["items"]
        sorted_predicates = priority(predicates, predicates_rules)

        # For hanoi problem, reset each stage
        # For logistics problem, reset each stage
        for fname in gstate["reset_function"]:
            gstate[fname] = {}
        solvepredicates(sorted_predicates, object_dic_copy, predicates_rules, gstate)
        stage_dic["visualSprites"] = object_dic_copy
        if "stageName" not in stage:
            stage_dic["stageName"] = "Inital Stage"
            stage_dic["stageInfo"] = "No step information"
            stage_dic["cost"] = "No cost"

        else:
            stage_dic["stageName"] = stage["stageName"]
            stage_dic["stageInfo"] = stage["stageInfo"]
            stage_dic["cost"] = stage["cost"]

        result["visualStages"].append(stage_dic)

    result["subgoals"] = Subgoal.get_subgoal(stages, problem_dic[1]['goal'].copy(), actionlist.copy())

    return result


def add_custome_objects(object_dic, animation_profile):
    """
    This function will added the custom object to the obj_dic
    :param object_dic: a object dictionary contain the default objects.
    :param animation_profile: a dict to store all information in animation profile.
    :return:
    """
    for visual in animation_profile["objects"]["custom"]:
        objects = animation_profile["objects"]["custom"][visual]
        for obj_name in objects:
            object_dic[obj_name] = animation_profile["visual"][visual].copy()
            object_dic[obj_name]["name"] = obj_name


def get_visualisation_dic(predicates, animation_profile, actionlist, problem_dic):
    """
    This function is the main function of this module, it will call the other functions
    to manipulate the visualisation file for the unity visualiser.
    :param predicates: an dictionary contains the 1.objects name and the 2.predicates for each stages.
    :param animation_profile: a dict to store all information in animation profile.
    :param actionlist: list of action to achieve the goal
    :param problem_dic: problem dictionary contain the init and goal predicates
    :return: dictionary contain all the solved stages for visualisation
    """

    object_list = copy.deepcopy(predicates["objects"])
    stages = copy.deepcopy(predicates["stages"])
    predicates_rules = animation_profile["predicates_rules"]
    objects_dic = Initialise.initialise_objects(object_list, animation_profile)
    gstate = Initialise.initialise_custom_functions()
    add_custome_objects(objects_dic, animation_profile)
    result = solve_all_stages(stages, objects_dic, predicates_rules, gstate, actionlist, problem_dic)

    return result
