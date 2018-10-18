"""This component generate the subgoal data"""


# -----------------------------Authorship-----------------------------------------
# -- Authors  : Ella
# -- Group    : Planning Visualisation
# -- Date     : 5/Oct/2018
# -- Version  : 1.0
# --------------------------------------------------------------------------------
# -----------------------------Reviewer-------------------------------------------
# -- Authors  : Yi Ding
# -- Group    : Planning Visualisation
# -- Date     : 17/Oct/2018
# -- Version  : 1.0
# --------------------------------------------------------------------------------


def get_subgoal(stages, final_goal, action_list):
    """
    :param stages: an dictionary that store all the solved position data
    :param final_goal: goal of the problem
    :param action_list: list of action to achieve the final goal
    :return: subgoal dictionary
    """
    stepNum = []
    stepindex = 1;
    # define subgoals dict
    subgoals = []
    finalstage = final_goal

    action_name_list = []
    for counter in range(0, len(action_list)):
        action_name = action_list[counter]['name']
        action_name_list.append(action_name)

    for stage in stages:
        if stage["stageName"] != "Initial Stage":

            for item in stage["items"]:
                if item in finalstage:
                    str = "(" + item["name"] + " "
                    for name in item["objectNames"]:
                        str = str + name + " "

                    str += ")"
                    objectlist = item["objectNames"]
                    stepNum.append(stepindex)
                    stepNames = action_name_list[stepindex - 1]
                    sub = {"name": str, "stepNum": stepindex, "stepName": stepNames, "objects": objectlist}
                    subgoals.append(sub)
            stepindex = stepindex + 1
        else:
            for item in stage["items"]:
                if item in finalstage:
                    str = "(" + item["name"] + " "
                    for name in item["objectNames"]:
                        str = str + name + " "
                    str += ")"
                    objectlist = item["objectNames"]
                    stepNames = "Initial Stage"
                    sub = {"name": str, "stepNum": 0, "stepName": stepNames, "objects": objectlist}
                    subgoals.append(sub)

    return subgoals
