"""Test the differential testing"""
from unittest import TestCase
import unittest

from cs9_autograder import (d_compare, d_compare_pairs, d_returned, d_method,
                            Autograder)

from .mixins import TestTester


class TestDifferential(TestTester, TestCase):
    def test_diff_function(self):
        def correct_func():
            return True

        def student_func():
            return False

        class Grader(Autograder):
            @d_returned(correct_func, student_func)
            def test(self, fn):
                return fn()

        self.assertTestCaseFailure(Grader)

    def test_diff_function_with_compare(self):
        def correct_func():
            return 3

        def student_func():
            return 0.1 * 30

        class Grader(Autograder):
            @d_returned(correct_func, student_func,
                        assertion=Autograder.assertAlmostEqual)
            def test_0(self, fn):
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
            @d_returned(correct_func, student_func,
                        normalize=normalize)
            def test_0(self, fn):
                return fn()

        self.assertTestCaseNoFailure(Grader)

    def test_diff_func_arg(self):
        """Test the func argument for d_returned"""
        def correct_func():
            return True

        def student_func():
            return True

        class Grader(Autograder):
            test = d_returned(correct_func, student_func,
                       func=lambda _, f: f())

        self.assertTestCaseNoFailure(Grader)

    def test_d_returned_class_kwarg(self):
        """Test that the correct and student can be defined in the class
        instead."""
        def correct_func():
            return False

        def student_func():
            return True

        class Grader(Autograder, correct=correct_func,
                     student=student_func):
            @d_returned
            def test(self, fn):
                return fn()

        print(Grader.test)

        self.assertTrue(callable(Grader.test))

        self.assertTestCaseFailure(Grader)


class TestDifferentialMethod(TestTester, TestCase):
    def test_d_method(self):
        class Correct:
            def my_method(self):
                return 3

        class Student:
            def my_method(self):
                return 3

        class Grader(Autograder,
                     correct=Correct, student=Student,
                     method='my_method'):

            test = d_method()

        self.assertTestCaseNoFailure(Grader)

    def test_d_method_ctor_args(self):
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

        class Grader(Autograder,
                     correct=Correct, student=Student,
                     method='my_method'):

            test = d_method((3,))

        self.assertTestCaseNoFailure(Grader)

    def test_d_method_m_args(self):
        class Correct:
            def my_method(self, x, y):
                return x + y

        class Student:
            def my_method(self, x, y):
                return x - y

        class Grader(Autograder,
                     correct=Correct, student=Student,
                     method='my_method'):

            test = d_method(m_args=(1, 3,))

        self.assertTestCaseFailure(Grader)

    def test_d_method_args_and_kwargs(self):
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


        class Grader(Autograder,
                     correct=Correct, student=Student,
                     method='my_method'):

            test_0 = d_method((), {'a': 1},
                              ('a'), {'z': True})

        self.assertTestCaseNoFailure(Grader)


class TestDCompare(TestTester, TestCase):
    def test_d_compare_passing(self):
        class Correct:
            def __init__(self, value):
                self.value = value

            def __lt__(self, other):
                return self.value < other.value

        class Student:
            def __init__(self, value):
                self.value = value

            def __lt__(self, other):
                return self.value < other.value

        class Grader(Autograder,
                     correct=Correct, student=Student,
                     method='__lt__'):

            test_0 = d_compare((1,), (2,))

        self.assertTestCaseNoFailure(Grader)

    def test_d_compare_failing(self):
        class Correct:
            def __init__(self, value):
                self.value = value

            def __lt__(self, other):
                return self.value < other.value

        class Student:
            def __init__(self, value):
                self.value = value

            def __lt__(self, other):
                return self.value >= other.value

        class Grader(Autograder,
                     correct=Correct, student=Student,
                     method='__lt__'):

            test_0 = d_compare((1,), (2,))

        self.assertTestCaseFailure(Grader)

    def test_d_compare_bidirectional(self):
        class Correct:
            def __init__(self, value):
                self.value = value

            def __lt__(self, other):
                return self.value < other.value

        class Student:
            def __init__(self, value):
                self.value = value

            def __lt__(self, other):
                return True

        class Grader(Autograder, correct=Correct, student=Student,
                     method='__lt__'):

            test_0 = d_compare((1,), (2,), bidirectional=True)

        self.assertTestCaseFailure(Grader)


class TestDComparePairs(TestTester, TestCase):
    def test_d_compare_pairs_passing(self):
        class Grader(Autograder, correct=int, student=int,
                     method='__eq__'):
            test_0 = d_compare_pairs([('1',), ('2',), ('3',)])

        self.assertTestCaseNoFailure(Grader)

    def test_d_compare_pairs_failing(self):
        class Correct:
            def __init__(self, value):
                self.value = value

            def __eq__(self, other):
                return self.value == other.value

        class Student:
            def __init__(self, value):
                self.value = value

            def __eq__(self, other):
                return True

        class Grader(Autograder, correct=Correct, student=Student,
                     method='__eq__'):
            test_0 = d_compare_pairs([('1',), ('2',), ('3',)])

        self.assertTestCaseFailure(Grader)

    def test_d_compare_pairs_call_counts(self):
        ctor_args = [('1',), ('2',), ('3',)]

        class Correct:
            call_count = 0
            def __init__(self, value):
                self.value = value

            def __eq__(self, other):
                Correct.call_count += 1
                return self.value == other.value

        class Student:
            call_count = 0
            def __init__(self, value):
                self.value = value

            def __eq__(self, other):
                Student.call_count += 1
                return self.value == other.value

        class Grader(Autograder, correct=Correct, student=Student,
                     method='__eq__'):
            test_0 = d_compare_pairs(ctor_args)

        self.assertTestCaseNoFailure(Grader)

        # we need to do these tests after running Grader with
        # assertTestCaseNoFailure
        expected_call_count = len(ctor_args) ** 2
        self.assertEqual(expected_call_count, Correct.call_count)
        self.assertEqual(expected_call_count, Student.call_count)


    def test_d_compare_pairs_kwargs(self):
        test_case = self
        class Correct:
            def __init__(self, value=None):
                self.value = value

            def __eq__(self, other):
                return self.value == other.value

        class Student:
            def __init__(self, value=None):
                test_case.assertIsNotNone(value)
                self.value = value

            def __eq__(self, other):
                return self.value == other.value

        class Grader(Autograder, correct=Correct, student=Student,
                     method='__eq__'):
            test_0 = d_compare_pairs([((), {'value': 2}),
                                      ((1,), {})],
                                     has_kwargs=True)

        self.assertTestCaseNoFailure(Grader)
