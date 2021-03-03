"""This component transfer the subgoal data to the format that Unity visualiser could accept"""


# -----------------------------Authorship-----------------------------------------
# -- Authors  : Ella
# -- Group    : Planning Visualisation
# -- Date     : 5/Oct/2018
# -- Version  : 1.0
# --------------------------------------------------------------------------------
# -----------------------------Reviewer-------------------------------------------
# -- Authors  : Yi Ding
# -- Group    : Planning Visualisation
# -- Date     : 16/Oct/2018
# -- Version  : 1.1
# --------------------------------------------------------------------------------
def generate_subgoal(subgoals):
    """
    "This function transfers the subgoal structure to adapt the unity visualiser
    :param subgoals: original sugoal structure
    :return: new subgoal structure that can be used for our visualser
    """
    m_keys = []
    m_values = []
    for subgoal in dedupe(subgoals):
        m_keys.append(subgoal["name"])
        m_values.append(subgoal["objects"])
    subgoal_pool = {"m_keys": m_keys, "m_values": m_values}

    step_list = []
    values = []
    for subgoal in subgoals:
        if subgoal["stepNum"] not in step_list:
            step_list.append(subgoal["stepNum"])

    for step in step_list:
        value = []
        for subgoal in subgoals:
            if subgoal["stepNum"] == step:
                value.append(subgoal["name"])
        values.append(value)
    pool_map = {"m_keys": step_list, "m_values": values}
    subgoal_transfer = {"subgoalPool": subgoal_pool, "subgoalMap": pool_map}
    return subgoal_transfer


# def generate_subgoal(subgoals):
#     """
#     "This function transfers the subgoal structure to adapt the unity visualiser
#     :param subgoals: original sugoal structure
#     :return: new subgoal structure that can be used for our visualser
#     """
#     subgoal_pool = []
#     for subgoal in dedupe(subgoals):
#         temp = {subgoal["name"]: subgoal["objects"]}
#
#         subgoal_pool.append(temp)
#     print(subgoal_pool)
#     step_list = []
#     for subgoal in subgoals:
#         if subgoal["stepNum"] not in step_list:
#             step_list.append(subgoal["stepNum"])
#
#     subgoal_map = []
#     for step in step_list:
#         value = []
#         for subgoal in subgoals:
#             if subgoal["stepNum"] == step:
#
#                 value.append(subgoal["name"])
#         temp = {step: value}
#         subgoal_map.append(temp)
#     subgoal_transfer = {"subgoalPool": subgoal_pool,"subgoalMap": subgoal_map}
#     return subgoal_transfer


#######################################################
# This function is designed to combine the subgoal
# with the same name into one dict.
def dedupe(items):
    """
    The function is to group subgoal information
    :param items: raw subgoal list
    :return: grouped subgoal list
    """
    seen = []
    result = []

    for item in items:
        if item["name"] not in seen:
            seen.append(item["name"])
    for subgoal_name in seen:
        stepList = []
        stepNameList = []
        objectList = []
        for item in items:
            if item["name"] == subgoal_name:
                stepList.append(item["stepNum"])
                stepNameList.append(item["stepName"])
                objectList = item["objects"]
        result.append({"name": subgoal_name, "stepNum": stepList, "stepName": stepNameList, "objects": objectList})
    return result
