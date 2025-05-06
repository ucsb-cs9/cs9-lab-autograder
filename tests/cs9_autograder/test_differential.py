"""Test the differential testing"""
from unittest import TestCase
import unittest

from cs9_autograder import Autograder, differential


class TestTester():
    def assertTestCaseNoErrorOrFailure(self, test_case_class):
        """Run a TestCase and assert that it has no errors or failures."""
        result = unittest.TestResult()
        case = test_case_class()
        case.run(result)

        self.assertFalse(result.errors or result.failures,
                         msg=str(result))


class TestDifferential(TestCase, TestTester):
    def test_diff_function(self):
        def correct_func():
            return True

        def student_func():
            return False

        class Grader(Autograder):
            @unittest.expectedFailure
            @differential(correct_func, student_func)
            def runTest(self, fn):
                return fn()

        self.assertTestCaseNoErrorOrFailure(Grader)

    def test_diff_function_with_compare(self):
        def correct_func():
            return 3

        def student_func():
            return 0.1 * 30

        class Grader(Autograder):
            @differential(correct_func, student_func,
                          assertion=Autograder.assertAlmostEqual)
            def runTest(self, fn):
                return fn()

        self.assertTestCaseNoErrorOrFailure(Grader)

    def test_diff_function_with_normalize(self):
        def correct_func():
            return "hello world"

        def student_func():
            return "  hello world\n"

        def normalize(text):
            return text.strip()

        class Grader(Autograder):
            @differential(correct_func, student_func,
                          normalize=normalize)
            def runTest(self, fn):
                return fn()

        self.assertTestCaseNoErrorOrFailure(Grader)
