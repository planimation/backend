"""This module is designed to help with getting a randomly selected color"""
# -----------------------------Authorship-----------------------------------------
# -- Authors  : Sai
# -- Group    : Planning Visualisation
# -- Date     : 13/August/2018
# -- Version  : 1.0
# --------------------------------------------------------------------------------
# -----------------------------Reviewer-------------------------------------------
# -- Authors  : Yi Ding
# -- Group    : Planning Visualisation
# -- Date     : 17/October/2018
# -- Version  : 1.0
# --------------------------------------------------------------------------------
import random

random_colorList = [{'r': 0.73, 'g': 1.0, 'b': 1.0, 'a': 1.0},
                    {'r': 0.4, 'g': 0.55, 'b': 0.55, 'a': 1.0},
                    {'r': 0.86, 'g': 0.86, 'b': 0.86, 'a': 1.0},
                    {'r': 1.0, 'g': 0.85, 'b': 0.73, 'a': 1.0},
                    {'r': 1.0, 'g': 0.98, 'b': 0.8, 'a': 1.0},
                    {'r': 0.94, 'g': 1.0, 'b': 0.94, 'a': 1.0},
                    {'r': 1.0, 'g': 0.89, 'b': 0.88, 'a': 1.0},
                    {'r': 0.0, 'g': 0.77, 'b': 0.8, 'a': 1.0},
                    {'r': 1.0, 'g': 0.5, 'b': 0.14, 'a': 1.0},
                    {'r': 1.0, 'g': 0.76, 'b': 0.76, 'a': 1.0},
                    {'r': 0.47, 'g': 0.53, 'b': 0.6, 'a': 1.0},
                    {'r': 0.5, 'g': 1.0, 'b': 0.83, 'a': 1.0},
                    {'r': 0.8, 'g': 0.52, 'b': 0.25, 'a': 1.0},
                    {'r': 0.93, 'g': 0.93, 'b': 0.0, 'a': 1.0},
                    {'r': 0.8, 'g': 0.4, 'b': 0.11, 'a': 1.0},
                    {'r': 0.41, 'g': 0.55, 'b': 0.41, 'a': 1.0},
                    {'r': 1.0, 'g': 0.76, 'b': 0.76, 'a': 1.0},
                    {'r': 0.42, 'g': 0.65, 'b': 0.8, 'a': 1.0},
                    {'r': 0.0, 'g': 0.55, 'b': 0.0, 'a': 1.0}]


# This function will provide a randomly selected color for Initialise to use.
def get_random_color():
    """
    This function random select an color from the predefine list of color
    :return: an random color
    """
    return random.choice(random_colorList)
