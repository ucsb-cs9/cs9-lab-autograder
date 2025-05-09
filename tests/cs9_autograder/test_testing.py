from io import StringIO
import os
from pathlib import Path
import unittest
from unittest import TestCase

from .mixins import (SubmissionPathRestorer, TestTester)

from cs9_autograder import (Autograder, t_coverage, set_submission_path,
                            t_module,
                            TestingAutograder, TestingReport)


class TestTestingAutograder(TestTester, SubmissionPathRestorer, TestCase):
    def setUp(self):
        super().setUp()

        script_dir = Path(__file__).resolve().parent
        self.test_path = script_dir / 'coverage_test_files'
        set_submission_path(self.test_path)

    def test_testing_autograder_coverage_failure(self):
        class Grader(TestingAutograder):
            test_test_file = t_module('testFile')
            test_coverage = t_coverage('failure_module')

        self.assertTestCaseFailure(Grader)

    def test_testing_autograder_coverage_success(self):
        class Grader(TestingAutograder):
            test_test_file = t_module('testFile')
            test_coverage = t_coverage('success_module')

        self.assertTestCaseNoFailure(Grader)

    def test_testing_autograder_coverage_no_tests(self):
        class Grader(TestingAutograder):
            test_test_file = t_module('testFile')
            test_coverage = t_coverage('no_tests_module')

        self.assertTestCaseFailure(Grader)

    def test_testing_autograder_cov_multiple_modules(self):
        """This is to test that run_pytest is building its `--cov` arguments
        correctly"""
        class Grader(TestingAutograder):
            test_test_file = t_module('testFile')
            test_cov_0 = t_coverage('failure_module')
            test_cov_1 = t_coverage('no_tests_module')

        self.assertTestCaseFailure(Grader, 2)


class TestTModule(TestTester, SubmissionPathRestorer, TestCase):
    def setUp(self):
        super().setUp()

        script_dir = Path(__file__).resolve().parent
        self.test_path = script_dir / 't_module_test_files'
        set_submission_path(self.test_path)

    def test_test_module_failing(self):
        class Grader(TestingAutograder):
            test = t_module('failing')

        self.assertTestCaseFailure(Grader)


class TestTestingReport(TestCase):
    def test_from_run(self):
        raw = [
                {"pytest_version": "5.2.2", "$report_type": "SessionStart"},
                {
                    "nodeid": "",
                    "outcome": "passed",
                    "longrepr": None,
                    "result": None,
                    "sections": [],
                    "$report_type": "CollectReport",
                },
                {
                    "nodeid": "test_report_example.py",
                    "outcome": "passed",
                    "longrepr": None,
                    "result": None,
                    "sections": [],
                    "$report_type": "CollectReport",
                },
                {
                    "nodeid": "test_report_example.py::test_ok",
                    "location": ["test_report_example.py", 0, "test_ok"],
                    "keywords": {"test_ok": 1, "pytest-reportlog": 1, "test_report_example.py": 1},
                    "outcome": "passed",
                    "longrepr": None,
                    "when": "setup",
                    "user_properties": [],
                    "sections": [],
                    "duration": 0.0,
                    "$report_type": "TestReport",
                },
                {
                    "nodeid": "test_report_example.py::test_ok",
                    "location": ["test_report_example.py", 0, "test_ok"],
                    "keywords": {"test_ok": 1, "pytest-reportlog": 1, "test_report_example.py": 1},
                    "outcome": "passed",
                    "longrepr": None,
                    "when": "call",
                    "user_properties": [],
                    "sections": [],
                    "duration": 0.0,
                    "$report_type": "TestReport",
                },
                {
                    "nodeid": "test_report_example.py::test_ok",
                    "location": ["test_report_example.py", 0, "test_ok"],
                    "keywords": {"test_ok": 1, "pytest-reportlog": 1, "test_report_example.py": 1},
                    "outcome": "passed",
                    "longrepr": None,
                    "when": "teardown",
                    "user_properties": [],
                    "sections": [],
                    "duration": 0.00099945068359375,
                    "$report_type": "TestReport",
                },
                {
                    "nodeid": "test_report_example.py::test_fail",
                    "location": ["test_report_example.py", 4, "test_fail"],
                    "keywords": {
                        "test_fail": 1,
                        "pytest-reportlog": 1,
                        "test_report_example.py": 1,
                    },
                    "outcome": "passed",
                    "longrepr": None,
                    "when": "setup",
                    "user_properties": [],
                    "sections": [],
                    "duration": 0.0,
                    "$report_type": "TestReport",
                },
                {
                    "nodeid": "test_report_example.py::test_fail",
                    "location": ["test_report_example.py", 4, "test_fail"],
                    "keywords": {
                        "test_fail": 1,
                        "pytest-reportlog": 1,
                        "test_report_example.py": 1,
                    },
                    "outcome": "failed",
                    "longrepr": {
                        "reprcrash": {
                            "path": "D:\\projects\\pytest-reportlog\\test_report_example.py",
                            "lineno": 6,
                            "message": "assert (4 + 4) == 1",
                        },
                        "reprtraceback": {
                            "reprentries": [
                                {
                                    "type": "ReprEntry",
                                    "data": {
                                        "lines": [
                                            "    def test_fail():",
                                            ">       assert 4 + 4 == 1",
                                            "E       assert (4 + 4) == 1",
                                        ],
                                        "reprfuncargs": {"args": []},
                                        "reprlocals": None,
                                        "reprfileloc": {
                                            "path": "test_report_example.py",
                                            "lineno": 6,
                                            "message": "AssertionError",
                                        },
                                        "style": "long",
                                    },
                                }
                            ],
                            "extraline": None,
                            "style": "long",
                        },
                        "sections": [],
                        "chain": [
                            [
                                {
                                    "reprentries": [
                                        {
                                            "type": "ReprEntry",
                                            "data": {
                                                "lines": [
                                                    "    def test_fail():",
                                                    ">       assert 4 + 4 == 1",
                                                    "E       assert (4 + 4) == 1",
                                                ],
                                                "reprfuncargs": {"args": []},
                                                "reprlocals": None,
                                                "reprfileloc": {
                                                    "path": "test_report_example.py",
                                                    "lineno": 6,
                                                    "message": "AssertionError",
                                                },
                                                "style": "long",
                                            },
                                        }
                                    ],
                                    "extraline": None,
                                    "style": "long",
                                },
                                {
                                    "path": "D:\\projects\\pytest-reportlog\\test_report_example.py",
                                    "lineno": 6,
                                    "message": "assert (4 + 4) == 1",
                                },
                                None,
                            ]
                        ],
                    },
                    "when": "call",
                    "user_properties": [],
                    "sections": [],
                    "duration": 0.0009992122650146484,
                    "$report_type": "TestReport",
                },
                {
                    "nodeid": "test_report_example.py::test_fail",
                    "location": ["test_report_example.py", 4, "test_fail"],
                    "keywords": {
                        "test_fail": 1,
                        "pytest-reportlog": 1,
                        "test_report_example.py": 1,
                    },
                    "outcome": "passed",
                    "longrepr": None,
                    "when": "teardown",
                    "user_properties": [],
                    "sections": [],
                    "duration": 0.0,
                    "$report_type": "TestReport",
                },
                {"exitstatus": 1, "$report_type": "SessionFinish"},
            ]

        test_report = TestingReport.from_raw("", raw)

        self.assertFalse(test_report.success)

        expected_failed = {'test_report_example.py::test_fail'}
        self.assertEqual(expected_failed, test_report.failed_tests)
