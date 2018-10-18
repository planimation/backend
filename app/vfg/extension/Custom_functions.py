# -----------------------------Authorship-----------------------------------------
# -- Authors  : Yi Ding
# -- Group    : Planning Visualisation
# -- Date     : 16/Sep/2018
# -- Version  : 2.0
# --------------------------------------------------------------------------------
# -----------------------------Reviewer-------------------------------------------
# -- Authors  : Yi Ding & Ella
# -- Group    : Planning Visualisation
# -- Date     : 17/Oct/2018
# -- Version  : 2.1
# --------------------------------------------------------------------------------
import re
import numpy as np

"""This module contain all the customer funtion we designed to help position the objects"""


def customf_controller(fname, obj_list, settings, state, remove, get_meta=False):
    """
    This function is an controller to call the different custom function
    :param fname: funtion name
    :param obj_list: object dictionary which contain all the information needed
    :param settings: custom setting for the function
    :param state: current state(a dictionary) of the function
    :param remove: whether it is an remove operation(this param is designed for future use)
    :param get_meta: boolean to indicate whether return the meta data about the custom function
    :return: the updated position dictionary and the state of the custom function
    """
    if fname == "distributex":
        return distributex(obj_list, settings, state, remove, get_meta)
    elif fname == "distribute_grid_around_point":
        return distribute_grid_around_point(obj_list, settings, state, remove, get_meta)
    elif fname == "distribute_within_objects_vertical":
        return distribute_within_objects_vertical(obj_list, settings, state, remove, get_meta)
    elif fname == "apply_smaller":
        return apply_smaller(obj_list, settings, state, remove, get_meta)
    elif fname == "align_middle":
        return align_middle(obj_list, settings, state, remove, get_meta)
    elif fname == "distributey":
        return distributey(obj_list, settings, state, remove, get_meta)
    elif fname == "distribute_within_objects_horizontal":
        return distribute_within_objects_horizontal(obj_list, settings, state, remove, get_meta)
    elif fname == "calculate_label":
        return calculate_label(obj_list, settings, state, remove, get_meta)
    elif fname == "draw_line":
        return draw_line(obj_list, settings, state, remove, get_meta)


def get_all_funtion_name():
    """
    This function returns all the available custom function
    :return: a list of custom function name
    """
    function_name = ["distributex", "distribute_grid_around_point", "distribute_within_objects_vertical",
                     "apply_smaller",
                     "align_middle", "distributey", "distribute_within_objects_horizontal", "calculate_label",
                     "draw_line"]
    return function_name


def distributex(obj_list, settings, state, remove, get_meta):
    """
    This funtion will return the x position of an object. used for block domain
    :param obj_list: Array of objects dictionary
    :param settings: a dictionary for settings
    :param state: state of the world
    :param remove: whether remove the object from the state
    :param get_meta: whether return the meta data
    :return: updated attribute dictionary and state
    """

    if get_meta:
        meta = {}
        meta["reset"] = False
        meta["require"] = {}
        return meta

    # initialise the state if it is empty
    if not state:
        state = [0]

    default_setting = {
        "spacebtw": 20
    }
    # update default settings
    for setting in default_setting:
        if setting in settings:
            default_setting[setting] = settings[setting]

    if len(obj_list) > 1:
        return False

    result = {
        "x": False
    }
    # object name and it's property dictionary
    obj, objdic = list(obj_list[0].items())[0]
    width = objdic["width"]
    if not remove:
        if obj in state:
            objindex = state.index(obj)
            result["x"] = objindex * (width + default_setting["spacebtw"])
            return result, state
        else:
            for num, value in enumerate(state):
                if num == value:
                    state[num] = obj
                    state.append(num + 1)
                    result["x"] = num * (width + default_setting["spacebtw"])
                    return result, state
    else:
        if obj in state:
            objindex = state.index(obj)
            state[objindex] = objindex
            return True
    return False


def distributey(obj_list, settings, state, remove, get_meta):
    """
    The function return the y location of object based on the number in object name
    :param obj_list:  Array of objects dictionary
    :param settings: a dictionary for settings
    :param state: state of the world
    :param remove: whether remove the object from the state
    :param get_meta: whether return the meta data
    :return: updated attribute dictionary and state
    """

    if get_meta:
        meta = {}
        meta["reset"] = False
        meta["require"] = {}
        return meta

    default_setting = {
        "spacebtw": 20,
        "initial": 0  # For default, number in object name start from 0
    }

    # update default settings
    for setting in default_setting:
        if setting in settings:
            default_setting[setting] = settings[setting]

    result = {
        "y": False
    }
    obj, objdic = list(obj_list[0].items())[0]

    row = int(re.findall('\d+', obj)[0]) - default_setting["initial"]
    result["y"] = row * (objdic["height"] + default_setting["spacebtw"])
    return result, state


def distribute_grid_around_point(obj_list, settings, state, remove, get_meta):
    """
    The function return the x location of object based on the number in object name, Node1-2,etc.
    :param obj_list: Array of objects dictionary
    :param settings: a dictionary for settings
    :param state:  state of the world
    :param remove: whether remove the object from the state
    :param get_meta: whether return the meta data
    :return: updated attribute dictionary and state
    """

    if get_meta:
        meta = {}
        meta["reset"] = False
        meta["require"] = {}
        return meta

    # default function settings
    default_setting = {
        "rowindex": 0,
        "colindex": 1,
        "margin": 100
    }
    # update default settings
    for setting in default_setting:
        if setting in settings:
            default_setting[setting] = settings[setting]

    result = {
        "x": False,
        "y": False,
    }

    # object name
    obj, objdic = list(obj_list[0].items())[0]
    row = int(re.findall('\d+', obj)[default_setting["rowindex"]])
    col = int(re.findall('\d+', obj)[default_setting["colindex"]])
    result["x"] = row * default_setting["margin"]
    result["y"] = col * default_setting["margin"]
    return result, state


def draw_line(obj_list, settings, state, remove, get_meta):
    """
    This function return an line object and its rotation angle. Any the line from (x1,y1) to (x2,y2)
    can be represent as horizontal line with rotation.
    :param obj_list: Array of objects dictionary
    :param settings: a dictionary for settings
    :param state: state of the world
    :param remove: whether remove the object from the state
    :param get_meta: whether return the meta data
    :return: a line object
    """

    if get_meta:
        meta = {}
        meta["reset"] = False
        meta["require"] = {
            "0": ["x", "y", "width", "height"],
            "1": ["x", "y", "width", "height"],
        }
        return meta

    # default function settings
    default_setting = {
        "prefabImage": "line"
    }

    # update default settings
    for setting in default_setting:
        if setting in settings:
            default_setting[setting] = settings[setting]

    if len(obj_list) != 2:
        return False

    # object name
    obj1, obj1dic = list(obj_list[0].items())[0]
    obj2, obj2dic = list(obj_list[1].items())[0]

    x1 = obj1dic["x"] + obj1dic["width"] / 2
    y1 = obj1dic["y"] + obj1dic["height"] / 2
    x2 = obj2dic["x"] + obj2dic["width"] / 2
    y2 = obj2dic["y"] + obj2dic["height"] / 2
    name = "line" + obj1 + obj2

    vec1 = np.array([1, 0])
    vec2 = np.array([x2 - x1, y2 - y1])
    Lvec1 = np.sqrt(vec1.dot(vec1))
    Lvec2 = np.sqrt(vec2.dot(vec2))
    middle = [(x1 + x2) / 2, (y1 + y2) / 2]
    lx1 = middle[0] - Lvec2 / 2
    ly1 = middle[1]
    cross = np.cross(vec1, vec2)
    cos_angle = vec1.dot(vec2) / (Lvec1 * Lvec2)
    radius = np.arccos(cos_angle)

    angle = radius * 360 / 2 / np.pi

    if cross <= 0:
        fangle = angle
    elif cross > 0:
        fangle = 360 - angle

    line = {}
    line["width"] = Lvec2
    line["rotate"] = fangle
    line["x"] = lx1
    line["y"] = ly1
    line["showName"] = False
    line["prefabImage"] = default_setting["prefabImage"]
    line["color"] = {"r": 0, "g": 0, "b": 0, "a": 1}
    line["height"] = 5
    line["name"] = name
    line["depth"] = 0
    return name, line


def distribute_within_objects_vertical(obj_list, settings, state, remove, get_meta):
    """
    The function return an x and y location of obj based on the location of parent

    :param obj_list: Array of objects dictionary
    :param settings: a dictionary for settings
    :param state: state of the world
    :param remove: whether remove the object from the state
    :param get_meta: whether return the meta data
    :return:  updated attribute dictionary and state
    """

    if get_meta:
        meta = {}
        meta["reset"] = False
        meta["require"] = {
            "0": ["width", "height"],
            "1": ["x", "y"],
        }
        return meta

    # default function settings
    default_setting = {
        "padding": 5,
        "row_count": 4
    }
    # update default settings
    for setting in default_setting:
        if setting in settings:
            default_setting[setting] = settings[setting]

    if len(obj_list) != 2:
        return False

    result = {
        "x": False,
        "y": False
    }

    # object name
    obj, objdic = list(obj_list[0].items())[0]
    parent, parentdic = list(obj_list[1].items())[0]

    # initalise state for parent
    if parent not in state:
        state[parent] = [0]

    row_count = default_setting["row_count"]
    padding = default_setting["padding"]

    if obj in state[parent]:
        objindex = state[parent].index(obj)
        result["x"] = parentdic["x"] + int(objindex / row_count) * objdic["width"] + padding
        result["y"] = parentdic["y"] + (objindex % row_count) * objdic["height"] + padding
        return result, state
    else:
        for num, value in enumerate(state[parent]):
            if num == value:
                state[parent][num] = obj
                state[parent].append(num + 1)
                # print(obj_dic[parent]["x"]+int(num/row_count)*obj["width"]+padding)
                result["x"] = parentdic["x"] + int(num / row_count) * objdic["width"] + padding
                result["y"] = parentdic["y"] + (num % row_count) * objdic["height"] + padding
                return result, state


def distribute_within_objects_horizontal(obj_list, settings, state, remove, get_meta):
    """
    The function return x location of obj based on the location of parent
    :param obj_list: Array of objects dictionary
    :param settings: a dictionary for settings
    :param state: state of the world
    :param remove: whether remove the object from the state
    :param get_meta: whether return the meta data
    :return: updated attribute dictionary and state
    """

    if get_meta:
        meta = {}
        meta["reset"] = False
        meta["require"] = {
            "0": ["width"],
            "1": ["x"],
        }
        return meta

    # default function settings
    default_setting = {
        "padding": 40,
        "col_count": 4
    }

    # update default settings
    for setting in default_setting:
        if setting in settings:
            default_setting[setting] = settings[setting]

    if len(obj_list) != 2:
        return False

    result = {
        "x": False
    }
    obj, objdic = list(obj_list[0].items())[0]
    parent, parentdic = list(obj_list[1].items())[0]

    # initalise state for parent
    if parent not in state:
        state[parent] = [0]

    padding = default_setting["padding"]

    if obj in state[parent]:
        objindex = state[parent].index(obj)
        result["x"] = parentdic["x"] + objindex * (objdic["width"] + padding)
        return result, state
    else:
        for num, value in enumerate(state[parent]):
            if num == value:
                state[parent][num] = obj
                state[parent].append(num + 1)
                result["x"] = parentdic["x"] + num * (objdic["width"] + padding)
                return result, state


def apply_smaller(obj_list, settings, state, remove, get_meta):
    """
    The function return width of object, it remember how big the object are by integer.Used for hanoi domain
    :param obj_list: Array of objects dictionary
    :param settings: a dictionary for settings
    :param state: state of the world
    :param remove: whether remove the object from the state
    :param get_meta: whether return the meta data
    :return: updated attribute dictionary and state
    """

    if get_meta:
        meta = {}
        meta["reset"] = True
        meta["require"] = {
            "0": ["width"]
        }
        return meta

    # default function settings
    default_setting = {
        "increase_width": 10,
    }
    # update default settings
    for setting in default_setting:
        if setting in settings:
            default_setting[setting] = settings[setting]

    if len(obj_list) != 2:
        return False

    result = {
        "width": False
    }
    # object name and its property dictionary
    obj1, obj1dic = list(obj_list[0].items())[0]
    obj2, obj2dic = list(obj_list[1].items())[0]
    # remove the digital char
    obj1type = ''.join(filter(lambda x: x.isalpha(), obj1))
    obj2type = ''.join(filter(lambda x: x.isalpha(), obj2))

    if obj1type == obj2type and obj1 != obj2:
        if obj1 not in state:
            state[obj1] = 1
        else:
            state[obj1] = state[obj1] + 1
        obj1dic["width"]= obj1dic["width"] + default_setting["increase_width"]
        result["width"]=obj1dic["width"]
        return result, state
    else:
        result["width"] = obj1dic["width"]
        return result, state


def calculate_label(obj_list, settings, state, remove, get_meta):
    """
    The function return the label of the objects, e.g showing how many packages in the trunks/airplane
    :param obj_list: Array of objects dictionary
    :param settings: a dictionary for settings
    :param state: state of the world
    :param remove: whether remove the object from the state
    :param get_meta: whether return the meta data
    :return: updated attribute dictionary and state
    """

    if get_meta:
        meta = {}
        meta["reset"] = True
        meta["require"] = {
        }
        return meta

    result = {
        "label": False
    }
    obj2, obj2dic = list(obj_list[1].items())[0]
    if obj2 not in state:
        state[obj2] = 1
        result["label"] = 1
    else:
        state[obj2] = state[obj2] + 1

        result["label"] = str(state[obj2])
    return result, state


def align_middle(obj_list, settings, state, remove, get_meta):
    """
    The function return updated x position of obj1 based on obj2
    it will make sure the middle of two object are aligned
    :param obj_list: Array of objects dictionary
    :param settings: a dictionary for settings
    :param state: state of the world
    :param remove: whether remove the object from the state
    :param get_meta: whether return the meta data
    :return: updated attribute dictionary and state
    """

    if get_meta:
        meta = {}
        meta["reset"] = False
        meta["require"] = {
            "0": ["width"],
            "1": ["x", "width"],
        }
        return meta

    if len(obj_list) != 2:
        return False

    result = {
        "x": False
    }
    # object name and its property dictionary
    obj1, obj1dic = list(obj_list[0].items())[0]
    obj2, obj2dic = list(obj_list[1].items())[0]

    result["x"] = obj2dic["x"] + (obj2dic["width"] - obj1dic["width"]) / 2
    return result, state
