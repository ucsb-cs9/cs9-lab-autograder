"""Test the differential testing"""
from unittest import TestCase
import unittest

from cs9_autograder import (Autograder, differential, differential_method,
                            DifferentialMethodAutograder)


class TestTester():
    def assertTestCaseNoFailure(self, test_case_class):
        """Run a TestCase and assert that it has no errors or failures."""
        self.assertTestCaseFailure(test_case_class, failures=0)


    def assertTestCaseFailure(self, test_case_class, failures=1):
        """Run a TestCase and assert that it has a particular amount of
        failures."""
        loader = unittest.TestLoader()
        test_suite = loader.loadTestsFromTestCase(test_case_class)

        result = unittest.TestResult()
        test_suite.run(result)

        error_msg = '\n'.join(x[1] for x in result.errors)
        self.assertEqual(0, len(result.errors), msg=error_msg)

        failure_msg = '\n'.join(x[1] for x in result.failures)
        self.assertEqual(failures, len(result.failures), msg=failure_msg)


class TestDifferential(TestCase, TestTester):
    def test_diff_function(self):
        def correct_func():
            return True

        def student_func():
            return False

        class Grader(Autograder):
            @differential(correct_func, student_func)
            def runTest(self, fn):
                return fn()

        self.assertTestCaseFailure(Grader)

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

        self.assertTestCaseNoFailure(Grader)

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

        self.assertTestCaseNoFailure(Grader)


class TestDifferentialMethod(TestCase, TestTester):
    def test_differential_method(self):
        class Correct:
            def my_method(self):
                return 3

        class Student:
            def my_method(self):
                return 3

        class Grader(DifferentialMethodAutograder,
                     correct_class=Correct, student_class=Student,
                     method_name='my_method'):

            runTest = differential_method()

        self.assertTestCaseNoFailure(Grader)

    def test_differential_method_ctor_args(self):
        class Correct:
            def __init__(self, value):
                self.value = value

            def my_method(self):
                return self.value

        class Student:
            def __init__(self, value):
                self.value = value

            def my_method(self):
                return self.value

        class Grader(DifferentialMethodAutograder,
                     correct_class=Correct, student_class=Student,
                     method_name='my_method'):

            runTest = differential_method((3,))

        self.assertTestCaseNoFailure(Grader)

    def test_differential_method_m_args(self):
        class Correct:
            def my_method(self, x, y):
                return x + y

        class Student:
            def my_method(self, x, y):
                return x - y

        class Grader(DifferentialMethodAutograder,
                     correct_class=Correct, student_class=Student,
                     method_name='my_method'):

            runTest = differential_method(m_args=(1, 3,))

        self.assertTestCaseFailure(Grader)

    def test_differential_method_args_and_kwargs(self):
        class Correct:
            def __init__(self, a=None):
                self.a = a

            def my_method(self, x, z=False):
                return f'{self.a} {x} {z}'

        class Student:
            def __init__(self, a=None):
                self.a = a
            def my_method(self, x, z=False):
                # hardcoded last item to double check we're setting the
                # kwargs properly
                return f'1 {x} True'


        class Grader(DifferentialMethodAutograder,
                     correct_class=Correct, student_class=Student,
                     method_name='my_method'):

            runTest = differential_method((), {'a': 1},
                                          ('a'), {'z': True})

        self.assertTestCaseNoFailure(Grader)
