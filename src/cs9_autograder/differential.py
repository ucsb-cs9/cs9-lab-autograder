from collections.abc import Callable, Iterable, Mapping
from types import MethodType
from typing import Any, Optional, Union


from .autograder import Autograder


def differential(correct_items: Any, student_items: Any,
                 assertion: Optional[Callable[..., None]] = None,
                 normalize: Optional[Callable[[Any], Any]] = None,
                 msg: Optional[str] = None):
    """A decorator to which converts a function into a differential test.

    The decorated function is called twice. First with correct_items, then
    with student_items.
    The returned values of the decorated function are then compared to
    determine if the student's implementation is correct.

    assertion: The method to call instead of assertEqual
    normalize: A function which normalizes the two returned values before
        comparison.
    msg: The msg to be passed to the assertion method.
    """

    def decorator(wrapped_method):
        def wrapper(self):
            expected = wrapped_method(self, correct_items)
            actual = wrapped_method(self, student_items)

            if normalize:
                expected = normalize(expected)
                actual = normalize(actual)

            if assertion:
                assertion(self, expected, actual, msg=msg)

            else:
                self.assertEqual(expected, actual, msg=msg)

        return wrapper
    return decorator



class DifferentialMethodAutograder(Autograder):
    def __init_subclass__(cls, /, correct_class, student_class, method_name,
                          weight=None,
                          **kwargs):
        super().__init_subclass__(**kwargs)
        cls.correct_class = correct_class
        cls.student_class = student_class
        cls.method_name = method_name
        cls.default_weight = weight


class differential_method:
    def __init__(self, ctor_args: Optional[tuple] = None,
                 ctor_kwargs: Optional[Mapping[str, Any]] = None,
                 m_args: Optional[tuple] = None,
                 m_kwargs: Optional[Mapping[str, Any]] = None):

        self.ctor_args = ctor_args if ctor_args else ()
        self.ctor_kwargs = ctor_kwargs if ctor_kwargs else {}

        self.m_args = m_args if m_args else ()
        self.m_kwargs = m_kwargs if m_kwargs else {}

    def __get__(self, instance, owner):
        @differential(owner.correct_class, owner.student_class)
        def runner(grader_self, tested_class):
            obj = tested_class(*self.ctor_args, **self.ctor_kwargs)
            tested_method = getattr(obj, owner.method_name)
            return tested_method(*self.m_args, **self.m_kwargs)

        # we have to wrap the runner and pass the instance because our
        # returned function isn't bound as a method by default
        return lambda: runner(instance)
