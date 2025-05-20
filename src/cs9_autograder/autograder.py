import traceback
import unittest
from typing import Any, Optional

from .formatting import h_rule, quoted_listing
from .importing import (FAILED_IMPORTS, module_to_path, path_to_module,
                        submission_path)
from .testing_report import CoverageReport, TestingReport
from .testing import run_unit_tests_and_coverage, t_coverage, t_module


class Autograder(unittest.TestCase):
    """The base class that all test cases will be derived from"""
    correct: Any
    student: Any
    method: Optional[str]
    weight: Optional[int]
    testing_report: Optional[TestingReport]
    cov_report = Optional[CoverageReport]


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

        cls.testing_report = None
        cls.cov_report = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._run_tests_and_coverage()

    @classmethod
    def _run_tests_and_coverage(cls):
        cov_modules = cls._coverage_modules()

        test_module = None
        try:
            test_module = cls._test_module()
        except ValueError:  # there is no test module
            if cov_modules:
                raise ValueError("Cannot check coverage when there is no"
                                 "test module spplied.")

        # only run unit tests if specified in the autograder
        if test_module:
            cls.testing_report, cls.cov_report = run_unit_tests_and_coverage(
                test_module, cov_modules, submission_path())

    @classmethod
    def _coverage_modules(cls) -> set[str]:
        """Get file names that we want to test the coverage for."""

        cov_modules = set()
        for attr in vars(cls).values():
            if isinstance(attr, t_coverage):
                cov_modules.add(attr.module_name)

        return cov_modules

    @classmethod
    def _test_module(cls) -> str:
        """Get module that we want to test the coverage for."""

        mod = None
        for attr in vars(cls).values():
            if isinstance(attr, t_module):
                if mod:
                    raise ValueError("Only one t_module is supported in "
                                     "TestingAutograder")
                mod = attr.module_name

        if not mod:
            raise ValueError("TestingAutograder must have one t_module.")

        return mod

    def test_student_imports(self):
        """test_student_imports: Checking for failed imports."""
        if not FAILED_IMPORTS:
            return

        files = set(x.filename for x in FAILED_IMPORTS)
        print('Failed to import the following files: '
              f'[{quoted_listing(files)}].')
        print()

        missing = set(x.filename for x in FAILED_IMPORTS if x.missing)
        if missing:
            print('The following files appear to be missing: '
                  f'[{quoted_listing(missing)}]')

            print('Make sure you have submitted the correct files and '
                  'that you have named your files properly.')
            print()

        exception = files - missing
        if exception:
            print('An exception occured while importing the following files:'
                  f'[{quoted_listing(exception)}]')
            print()

        for failed in FAILED_IMPORTS:
            h_rule()
            print(f"While importing '{failed.filename}':")

            # we are limiting the traceback to 1 because we don't want the
            # student to use the autograder as a debugger, or get confused
            # by the inclusion of autograder code in the traceback
            traceback.print_exception(failed.err, limit=1)

        self.fail()
