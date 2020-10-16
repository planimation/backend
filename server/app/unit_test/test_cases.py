import unittest
import re
import sys
import os
import json
import filecmp

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../vfg/' + "parser"))
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../vfg/' + "solver"))
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../vfg/' + "adapter/visualiser_adapter"))
import Parser_Functions, Animation_parser, Domain_parser, Plan_generator, Initialise, Solver
from Problem_parser import *
from Predicates_generator import *

import Solver, Initialise
import Transfer

class TestStringMethods(unittest.TestCase):

    def test_upper(self):
        #print(Parser_Functions.parse_objects('test'))
        self.assertEqual('foo'.upper(), 'FOO')

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)

    def test_visitall(self):
        url_link = ''
        animation_content = open(os.path.abspath(os.path.dirname(__file__) + '/../unit_test/' + 'domain_ap.pddl'), 'r', encoding='utf-8-sig').read()
        domain_content = open(os.path.abspath(os.path.dirname(__file__) + '/../unit_test/' + 'domain.pddl'), 'r', encoding='utf-8-sig').read().lower()
        problem_content = open(os.path.abspath(os.path.dirname(__file__) + '/../unit_test/' + 'problem.pddl'), 'r', encoding='utf-8-sig').read().lower()

        plan = Plan_generator.get_plan(domain_content, problem_content, url_link)

        predicates_list = Domain_parser.get_domain_json(domain_content)
        problem_dic = get_problem_dic(problem_content, predicates_list)
        object_list = get_object_list(problem_content)

        animation_profile = json.loads(Animation_parser.get_animation_profile(animation_content, object_list))

        stages = get_stages(plan, problem_dic, problem_content, predicates_list)

        result = Solver.get_visualisation_dic(stages, animation_profile, plan['result']['plan'], problem_dic)
        objects_dic = Initialise.initialise_objects(stages["objects"], animation_profile)
        final = Transfer.generate_visualisation_file(result, list(objects_dic.keys()), animation_profile, plan['result']['plan'])

        with open(os.path.abspath(os.path.dirname(__file__) + '/../unit_test/' + "test.vfg"), "w") as f:
            json.dump(final, f)

        output_content = open(os.path.abspath(os.path.dirname(__file__) + '/../unit_test/' + "test.vfg"), 'r', encoding='utf-8-sig').read()

        expected_content = open(os.path.abspath(os.path.dirname(__file__) + '/../unit_test/' + "expect_output.vfg"), 'r', encoding='utf-8-sig').read()
        #print(output_content, expected_content)

        self.assertTrue(filecmp.cmp(os.path.abspath(os.path.dirname(__file__) + '/../unit_test/' + 'test.vfg'), os.path.abspath(os.path.dirname(__file__) + '/../unit_test/' + 'expect_output.vfg'), shallow=False))

    def test_domain_parser(self):
        simple_domain_content = open(
            os.path.abspath(os.path.dirname(__file__) + '/../unit_test/' + 'domain.pddl'), 'r',
            encoding='utf-8-sig').read().lower()
        simple_predicates_list = Domain_parser.get_domain_json(simple_domain_content)
        # simple domain predicates:
        # (:predicates
        # (connected ?x ?y - place)
	    # (at-robot ?x - place)
	    # (visited ?x - place))
        simple_expected_predicates = {'connected': 2, 'at-robot': 1, 'visited': 1}
        self.assertTrue(simple_predicates_list == simple_expected_predicates)

        complex_domain_content = open(
            os.path.abspath(os.path.dirname(__file__) + '/../unit_test/' + '4_ops_domain.pddl'), 'r',
            encoding='utf-8-sig').read().lower()
        complex_predicates_list = Domain_parser.get_domain_json(complex_domain_content)
        # (:predicates
        # (on ?x ?y)
        # (ontable ?x)
        # (clear ?x)
        # (handempty)
        # (holding ?x))
        complex_expected_predicates = {'on': 2, 'ontable': 1, 'clear': 1, 'handempty': 0, 'holding' : 1}
        self.assertTrue(complex_predicates_list == complex_expected_predicates)

    def test_problem_parser(self):
        simple_problem_content = open(
            os.path.abspath(os.path.dirname(__file__) + '/../unit_test/' + '4_ops_problem.pddl'), 'r',
            encoding='utf-8-sig').read().lower()
        simple_domain_content = open(
            os.path.abspath(os.path.dirname(__file__) + '/../unit_test/' + '4_ops_domain.pddl'), 'r',
            encoding='utf-8-sig').read().lower()
        simple_predicates_list = Domain_parser.get_domain_json(simple_domain_content)
        simple_problem_list = get_problem_dic(simple_problem_content, simple_predicates_list)
        simple_expected_problem = [
            {'init': [
                {'name': 'on', 'objectNames': ['a', 'c']},
                {'name': 'ontable', 'objectNames': ['b']},
                {'name': 'ontable', 'objectNames': ['c']},
                {'name': 'clear', 'objectNames': ['a']},
                {'name': 'clear', 'objectNames': ['b']},
                {'name': 'handempty', 'objectNames': ['No objects']}]},
            {'goal': [
                {'name': 'on', 'objectNames': ['a', 'b']},
                {'name': 'on', 'objectNames': ['b', 'c']}],
            'goal-condition': ['and']}]
        self.assertTrue(simple_problem_list == simple_expected_problem)

        complex_problem_content = open(
            os.path.abspath(os.path.dirname(__file__) + '/../unit_test/' + 'problem.pddl'), 'r',
            encoding='utf-8-sig').read().lower()
        complex_domain_content = open(
            os.path.abspath(os.path.dirname(__file__) + '/../unit_test/' + 'domain.pddl'), 'r',
            encoding='utf-8-sig').read().lower()
        complex_predicates_list = Domain_parser.get_domain_json(complex_domain_content)
        complex_problem_list = get_problem_dic(complex_problem_content, complex_predicates_list)
        with open(os.path.abspath(os.path.dirname(__file__) + '/../unit_test/' + "complex_expected_problem.json"), "r") as f:
            complex_expected_problem = json.load(f)
        self.assertTrue(complex_expected_problem == complex_problem_list)

    def test_predicates_generator(self):
        simple_domain_content = open(os.path.abspath(os.path.dirname(__file__) + '/../unit_test/' + '4_ops_domain.pddl'), 'r',
                              encoding='utf-8-sig').read().lower()
        simple_problem_content = open(os.path.abspath(os.path.dirname(__file__) + '/../unit_test/' + '4_ops_problem.pddl'), 'r',
                               encoding='utf-8-sig').read().lower()
        simple_plan = Plan_generator.get_plan(simple_domain_content, simple_problem_content, '')
        simple_predicates_list = Domain_parser.get_domain_json(simple_domain_content)
        simple_problem_dic = get_problem_dic(simple_problem_content, simple_predicates_list)
        simple_object_list = get_object_list(simple_problem_content)
        simple_stages = get_stages(simple_plan, simple_problem_dic, simple_problem_content, simple_predicates_list)
        with open(os.path.abspath(os.path.dirname(__file__) + '/../unit_test/' + "simple_expected_stages.json"), "r") as f:
            simple_expected_stages = json.load(f)
        self.assertTrue(simple_stages == simple_expected_stages)

        complex_domain_content = open(
            os.path.abspath(os.path.dirname(__file__) + '/../unit_test/' + 'domain.pddl'), 'r',
            encoding='utf-8-sig').read().lower()
        complex_problem_content = open(
            os.path.abspath(os.path.dirname(__file__) + '/../unit_test/' + 'problem.pddl'), 'r',
            encoding='utf-8-sig').read().lower()
        complex_plan = Plan_generator.get_plan(complex_domain_content, complex_problem_content, '')
        complex_predicates_list = Domain_parser.get_domain_json(complex_domain_content)
        complex_problem_dic = get_problem_dic(complex_problem_content, complex_predicates_list)
        complex_object_list = get_object_list(complex_problem_content)
        complex_stages = get_stages(complex_plan, complex_problem_dic, complex_problem_content, complex_predicates_list)
        with open(os.path.abspath(os.path.dirname(__file__) + '/../unit_test/' + "complex_expected_stages.json"), "r") as f:
            complex_expected_stages = json.load(f)
        self.assertTrue(complex_stages == complex_expected_stages)

    def test_solver(self):
        # test initialise obj
        animation_content = open(os.path.abspath(os.path.dirname(__file__) + '/../unit_test/' + 'domain_ap.pddl'), 'r',
                                 encoding='utf-8-sig').read()
        problem_content = open(os.path.abspath(os.path.dirname(__file__) + '/../unit_test/' + 'problem.pddl'), 'r',
                               encoding='utf-8-sig').read().lower()
        object_list = get_object_list(problem_content)
        animation_profile = json.loads(Animation_parser.get_animation_profile(animation_content, object_list))
        initialised_obj_dict = Initialise.initialise_objects(object_list, animation_profile)
        with open(os.path.abspath(os.path.dirname(__file__) + '/../unit_test/' + "expected_initialised_obj_dict.json"), "r") as f:
            expected_initialised_obj_dict = json.load(f)
        self.assertTrue(initialised_obj_dict == expected_initialised_obj_dict)

        # testing check rule
        true_predicate = {'name': 'at-robot', 'objectNames': ['loc1_1']}
        false_predicate = {'name': 'at-robot', 'objectNames': ['loc1_2']}
        objects_dic = {
            'loc1_1': {'prefabimage': 'img-square', 'showname': False, 'x': 100, 'y': 100, 'color': {'r': 0.0, 'g': 0.0, 'b': 1.0, 'a': 1.0}, 'width': 80, 'height': 80, 'depth': 1, 'name': 'loc1_1'},
            'loc1_2': {'prefabimage': 'img-square', 'showname': False, 'x': 100, 'y': False, 'color': {'r': 0.0, 'g': 0.0, 'b': 1.0, 'a': 1.0}, 'width': 80, 'height': 80, 'depth': 1, 'name': 'loc1_2'},
            'robot': {'prefabimage': 'img-robot', 'showname': False, 'x': 100, 'y': 100, 'color': {'r': 0.9804, 'g': 0.6353, 'b': 0.7098, 'a': 1.0}, 'width': 40, 'height': 40, 'depth': 2, 'name': 'robot'}}
        predicates_rules = {'at-robot':
                                {'rules': ['rule1', 'rule2', 'rule3'],
                                 'rule1': {'left': {'robot': ['x']},'value': {'equal': {'?x': 'x'}}},
                                 'rule2': {'left': {'robot': ['y']}, 'value': {'equal': {'?x': 'y'}}},
                                 'rule3': {'left': {'?x': ['color']}, 'value': {'equal': {'r': 0.9804, 'g': 0.6353, 'b': 0.7098, 'a': 1.0}}},
                                 'require': {'?x': ['x', 'y']},
                                 'objects': ['?x'],
                                 'custom_obj': ['robot']}}
        self.assertTrue(Solver.check_rule_complete(true_predicate, objects_dic, predicates_rules))
        self.assertFalse(Solver.check_rule_complete(false_predicate, objects_dic, predicates_rules))

        # test get obj name
        property_dic = {'?x': ['property1', 'property2']}
        obj_ref_dic = {'?x': 'obj1'}
        expected_obj_name_prop = ('?x', 'obj1', ['property1', 'property2'])
        obj_name_prop = Solver.get_objname_property(property_dic, obj_ref_dic)
        self.assertTrue(expected_obj_name_prop == obj_name_prop)


if __name__ == '__main__':
    unittest.main()