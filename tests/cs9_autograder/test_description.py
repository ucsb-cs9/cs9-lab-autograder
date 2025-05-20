"""Test the descripiton picked up by Gradescope"""

import re
import unittest
from unittest import TestCase

from cs9_autograder import Autograder, d_compare


def get_description(test_case_class, test_name):
    class DummyJSONTestResult:
        descriptions = True

    loader = unittest.TestLoader()
    loader.testNamePatterns = [f'*.{test_name}']
    test_suite = loader.loadTestsFromTestCase(test_case_class)

    tests = list(test_suite)

    print(tests)
    if len(tests) != 1:
        raise ValueError("get_description expects test_case_class to have only"
                         " 1 test.")

    test = tests[0]

    # based on JSONTestResult.getDescripion from gradescope-utils
    doc_first_line = test.shortDescription()
    if doc_first_line:
        return doc_first_line
    else:
        return str(test)


class TestDocsstingDescription(TestCase):
    def test_docstring_description(self):
        class Grader(Autograder):
            def test_0(self):
                """My Test Description"""
                pass

        actual = get_description(Grader, 'test_0')
        expected = "My Test Description"
        self.assertEqual(expected, actual)


class TestDCompareDescription(TestCase):
    def test_d_compare_description(self):
        class Grader(Autograder,
                     correct=int, student=int,
                     method='__eq__'):

            test_0 = d_compare((1,), (2,))

        actual = get_description(Grader, 'test_0')
        expected_pattern = r'test_0 \((\w|[.<>])+\.Grader\.test_0\)'
        self.assertTrue(re.fullmatch(expected_pattern, actual))
