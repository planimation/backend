"""This module is designed to get all the predicates list from domain animation PDDL"""
#-----------------------------Authorship-----------------------------------------
#-- Authors  : Sai
#-- Group    : Planning Visualisation
#-- Date     : 13/August/2018
#-- Version  : 1.0
#--------------------------------------------------------------------------------
#-----------------------------Reviewer-------------------------------------------
#-- Authors  : Sharukh, Gang chen
#-- Group    : Planning Visualisation
#-- Date     : 23/August/2018
#-- Version  : 1.0
#--------------------------------------------------------------------------------
#-----------------------------Reviewer-------------------------------------------
#-- Authors  : Yi Ding
#-- Group    : Planning Visualisation
#-- Date     : 17/Oct/2018
#-- Version  : 1.0
#--------------------------------------------------------------------------------
import re


#######################################################
# Input File: A domain file
# Output : All the predicates in the given domain.pddl file
#######################################################

def get_domain_json(domain_text):
    """
    This function return a list of predicates in domain profile.
    :param domain_text: domain pddl text
    :return: a dictionary contain which key is the predicate name and value is the number of objects
    """
    try:
        patternPare = re.compile(r'\((.*?)\)')
        old_strPre = domain_text[domain_text.index("predicates") + len("predicates"):domain_text.index("action")]

        # zmff
        # replace the unnecessary arguments with space, for the sake of selecting the info needed
        # example: old = (predicate ?obj - (either a b) ?obj2 - (either c d ))
        #         new = (predicate ?obj  ?obj2 )
        new_strPre= re.sub(r'(\s+-\s*|-\s+)(((\w)+)|((\((\s|\w)*\))?))', ' ', old_strPre)
        # print("old strPre: " + str(old_strPre))
        # print("new strPre: " + str(new_strPre))
        namePare = patternPare.findall(new_strPre)
        # print("namePare: " + str(namePare))
        PredicateList = {}

        for name in namePare:
            if (name.find("?") != -1):
                indexQue = name.find("?")
                namePre = name[0:indexQue - 1]
                PredicateList[namePre] = name.count("?")
            else:
                PredicateList[name] = name.count("?")
        return PredicateList
    except:
        raise ValueError("Empty string found")