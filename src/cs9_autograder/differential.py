from collections.abc import Callable, Iterable, Mapping
import itertools
from functools import partial
from types import MethodType
from typing import Any, Callable, Optional, Union


from .autograder import Autograder
from .smart_decorator import SmartDecorator, TestItemDecorator
from .test_item import TestItem


class d_returned(TestItemDecorator):
    """Run a template function with a correct object and student object and
    compare the value returned from the template function."""

    def init(self,
             correct: Any = None, student: Any = None,
             assertion: Optional[Callable[..., None]] = None,
             normalize: Optional[Callable[[Any], Any]] = None,
             msg: Optional[str] = None,
             **kwargs):

        # set correct and student for TestItem
        # if they were given as positional argument
        if correct:
            self._correct = correct
        if student:
            self._student = student

        self.assertion = assertion
        self.normalize = normalize
        self.msg = msg

    def decorator(self):
        def wrapper(this):
            expected = self.decorated(this, self.correct)
            actual = self.decorated(this, self.student)

            if self.normalize:
                expected = self.normalize(expected)
                actual = self.normalize(actual)

            if self.assertion:
                self.assertion(this, expected, actual, msg=self.msg)

            else:
                this.assertEqual(expected, actual, msg=self.msg)
        return wrapper

    def __get__(cls, instance, owner=None):
        return super().__get__(instance, owner)


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
        def runner(owner_self, tested_class):
            obj = tested_class(*self.ctor_args, **self.ctor_kwargs)
            tested_method = getattr(obj, owner.method)
            return tested_method(*self.m_args, **self.m_kwargs)

        # we have to wrap the runner and pass the instance because our
        # returned function isn't bound as a method by default
        return lambda: runner(instance)


class d_compare(TestItem):
    """Compare two items"""
    x_kwargs: dict[str, Any]
    y_kwargs: dict[str, Any]

    def __init__(self, *args, bidirectional=False, **kwargs):

        super().__init__(**kwargs)

        if len(args) == 2:
            self.x_args, self.y_args = args
            self.x_kwargs = {}
            self.y_kwargs = {}

        elif len(args) == 4:
            self.x_args, self.x_kwargs, self.y_args, self.y_kwargs = args

        else:
            raise ValueError("d_compare must be called with the arguments "
                             "(x_args, y_args) or "
                             "(x_args, x_kwargs, y_args, y_kwargs).")

        self.bidirectional = bidirectional

    def __call__(self, instance):
        @d_returned(self.correct, self.student)
        def runner(grader_self, tested_class):
            obj_x = tested_class(*self.x_args, **self.x_kwargs)
            obj_y = tested_class(*self.y_args, **self.y_kwargs)

            method_name = self.method

            x_method = getattr(obj_x, method_name)

            if self.bidirectional:
                y_method = getattr(obj_y, method_name)

                return (x_method(obj_y), y_method(obj_x))

            else:
                return x_method(obj_y)

        return runner(instance)

    def __get__(self, instance, owner):
        super().__get__(instance, owner)

        return partial(self.__call__, instance)


class d_compare_pairs(TestItem):
    def __init__(self, ctor_args: list[tuple]
                                  | list[tuple[tuple, dict[str, Any]]],
                 has_kwargs: bool = False,
                 **kwargs):

        super().__init__(**kwargs)

        if not has_kwargs:
            ctor_args = [(x, {}) for x in ctor_args]

        self.ctor_args = ctor_args

    def __get__(self, instance, owner):
        super().__get__(instance, owner)

        def runner():
            for lhs, rhs in itertools.product(self.ctor_args, self.ctor_args):
                lhs_args, lhs_kwargs = lhs
                rhs_args, rhs_kwargs = rhs
                compare = d_compare(lhs_args, lhs_kwargs, rhs_args, rhs_kwargs,
                                    _outer_test_item=self)
                print(compare)
                compare(instance)

        # we have to wrap the runner and pass the instance because our
        # returned function isn't bound as a method by default
        return runner
