from enum import auto, Enum
from abc import ABC, abstractmethod

from .test_item import TestItem


SENTINEL = object()

class Modes(Enum):
    RAW_DECORATOR = auto()
    COMPOSED = auto()
    KWARGS_DECORATOR = auto()


class SmartDecorator(ABC):
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

    @abstractmethod
    def init(self, *args, **kwargs):
        """Children should implement this function instead of __init__ because
        we do weird stuff to detect what kind of decorator we are."""
        ...

    @abstractmethod
    def decorator(self):
        ...


    def __init__(self, _first=SENTINEL, *args, func=None, **kwargs):
        super().__init__()

        self.descriptor = False
        self.instance = None
        self.owner = None

        if callable(_first) and not (args or kwargs):
            # assume we were used as a bare decorator without any arguments
            self.mode = Modes.RAW_DECORATOR
            self.decorated = _first

        elif func:
            # we are manually composing functions instead of acting as a
            # decorator
            self.mode = Modes.COMPOSED
            self.decorated = func

        else:
            self.mode = Modes.KWARGS_DECORATOR

        if self.mode != Modes.RAW_DECORATOR and _first is not SENTINEL:
            # we'll assume _func was a posional argument
            args = (_first,) + args

        self.init(*args, **kwargs)

    def __call__(self, _first=SENTINEL, *args, **kwargs):
        print(self.mode)
        if self.mode == Modes.RAW_DECORATOR or self.mode == Modes.COMPOSED:
            if _first is not SENTINEL:
                # we'll assume _func was a posional argument
                args = (_first,) + args

            if self.descriptor:
                # we need to add the "this" argument
                args = (self.instance,) + args

            return self.decorator()(*args, **kwargs)

        self.decorated = _first
        return SmartDecoratorWrapper(self, self.decorator())

    def __get__(self, instance, owner=None):
        self.instance = instance
        self.descriptor = True
        return self


class SmartDecoratorWrapper:
    def __init__(self, smart_decorator, func):
        self.smart_decorator = smart_decorator
        self.func = func

    def __get__(self, instance, owner=None):
        # when self *is* a member of a class, we just return func bound to
        # instance
        return lambda: self.func(instance)

    def __call__(self, *args, **kwargs):
        # for when we wrap a function that is a not a member
        return self.func(*args, **kwargs)


class TestItemDecorator(SmartDecorator, TestItem):
    """A class which inherits from both SmartDecorator and TestItem.
    This is provided because SmartDecorator inheritance is tricky."""

    def __init__(self, *args, weight=None, **kwargs):
        SmartDecorator.__init__(self, *args, **kwargs)
        TestItem.__init__(self, weight=weight)
