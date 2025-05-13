from collections.abc import Callable, Iterable, Mapping
from types import MethodType
from typing import Any, Optional, Union


from .autograder import Autograder
from .smart_decorator import SmartDecorator


class d_returned(SmartDecorator):
    def init(self, correct: Any = None, student: Any = None,
                 assertion: Optional[Callable[..., None]] = None,
                 normalize: Optional[Callable[[Any], Any]] = None,
                 msg: Optional[str] = None,
                 weight: Optional[int] = None):

        super().init()

        print("init", correct, student)

        self._correct = correct
        self._student = student
        self.assertion = assertion
        self.normalize = normalize
        self.msg = msg
        self.weight = weight

    @property
    def correct(self):
        return self._correct if self._correct else self.instance.correct

    @property
    def student(self):
        return self._student if self._student else self.instance.student

    def decorator(self):
        print("decorator")
        def wrapper(this):
            print("wrapper", self.correct, self.student)
            expected = self.decorated(this, self.correct)
            actual = self.decorated(this, self.student)

            if self.normalize:
                expected = self.normalize(expected)
                actual = self.normalize(actual)

            print("Before assertion")

            if self.assertion:
                self.assertion(this, expected, actual, msg=self.msg)

            else:
                this.assertEqual(expected, actual, msg=self.msg)
        return wrapper



# def d_returned(correct_items: Any, student_items: Any,
#                  assertion: Optional[Callable[..., None]] = None,
#                  normalize: Optional[Callable[[Any], Any]] = None,
#                  msg: Optional[str] = None):
#     """A decorator to which converts a function into a differential test.
#
#     The decorated function is called twice. First with correct_items, then
#     with student_items.
#     The returned values of the decorated function are then compared to
#     determine if the student's implementation is correct.
#
#     assertion: The method to call instead of assertEqual
#     normalize: A function which normalizes the two returned values before
#         comparison.
#     msg: The msg to be passed to the assertion method.
#     """
#
#     def decorator(wrapped_method):
#         def wrapper(self):
#
#
#         return wrapper
#     return decorator



class DifferentialAutograder(Autograder):
    def __init_subclass__(cls, /, correct: Any = None, student: Any = None,
                          method: Optional[str] = None,
                          weight=None,
                          **kwargs):

        super().__init_subclass__(**kwargs)

        # We don't want the correct and student functions to get bound to cls,
        # so we have to wrap them in staticmethod
        cls.correct = staticmethod(correct)
        cls.student = staticmethod(student)

        cls.method = method
        cls.weight = weight


class d_method:
    def __init__(self, ctor_args: Optional[tuple] = None,
                 ctor_kwargs: Optional[Mapping[str, Any]] = None,
                 m_args: Optional[tuple] = None,
                 m_kwargs: Optional[Mapping[str, Any]] = None):

        self.ctor_args = ctor_args if ctor_args else ()
        self.ctor_kwargs = ctor_kwargs if ctor_kwargs else {}

        self.m_args = m_args if m_args else ()
        self.m_kwargs = m_kwargs if m_kwargs else {}

    def __get__(self, instance, owner):
        @d_returned(owner.correct, owner.student)
        def runner(grader_self, tested_class):
            obj = tested_class(*self.ctor_args, **self.ctor_kwargs)
            tested_method = getattr(obj, owner.method)
            return tested_method(*self.m_args, **self.m_kwargs)

        # we have to wrap the runner and pass the instance because our
        # returned function isn't bound as a method by default
        return lambda: runner(instance)
