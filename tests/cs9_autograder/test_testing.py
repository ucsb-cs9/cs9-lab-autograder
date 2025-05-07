from io import StringIO
import os
from pathlib import Path
import unittest
from unittest import TestCase

from .utils import (TestTester, get_submission_path_config,
                    restore_submission_path_config)

from cs9_autograder import (Autograder, t_coverage, set_submission_path,
                            test_file_runner,
                            TestingAutograder, TestingReport)


class TestTestingAutograder(TestCase, TestTester):
    def setUp(self):
        self.path_config = get_submission_path_config()

        script_dir = Path(os.path.dirname(os.path.realpath(__file__)))
        self.test_path = script_dir / 'coverage_test_files'
        set_submission_path(self.test_path)

    def tearDown(self):
        restore_submission_path_config(self.path_config)

    def test_testing_autograder_coverage_failure(self):
        class Grader(TestingAutograder, module='testFile'):
            test_coverage = t_coverage('failure_module')

        self.assertTestCaseFailure(Grader)

    def test_testing_autograder_coverage_success(self):
        class Grader(TestingAutograder, module='testFile'):
            test_coverage = t_coverage('success_module')

        self.assertTestCaseNoFailure(Grader)

    def test_testing_autograder_coverage_no_tests(self):
        class Grader(TestingAutograder, module='testFile'):
            test_coverage = t_coverage('no_tests_module')

        self.assertTestCaseFailure(Grader)



class TestTestFile(TestCase, TestTester):

    def test_test_file(self):
        class Grader(Autograder):
            test = test_file_runner('testFile')

        self.assertTestCaseFailure(Grader)


class TestTestingReport(TestCase):
    def test_from_run(self):
        log = StringIO(r"""{"pytest_version": "5.2.2", "$report_type": "SessionStart"}
{"nodeid": "", "outcome": "passed", "longrepr": null, "result": null, "sections": [], "$report_type": "CollectReport"}
{"nodeid": "test_report_example.py", "outcome": "passed", "longrepr": null, "result": null, "sections": [], "$report_type": "CollectReport"}
{"nodeid": "test_report_example.py::test_ok", "location": ["test_report_example.py", 0, "test_ok"], "keywords": {"test_ok": 1, "pytest-reportlog": 1, "test_report_example.py": 1}, "outcome": "passed", "longrepr": null, "when": "setup", "user_properties": [], "sections": [], "duration": 0.0, "$report_type": "TestReport"}
{"nodeid": "test_report_example.py::test_ok", "location": ["test_report_example.py", 0, "test_ok"], "keywords": {"test_ok": 1, "pytest-reportlog": 1, "test_report_example.py": 1}, "outcome": "passed", "longrepr": null, "when": "call", "user_properties": [], "sections": [], "duration": 0.0, "$report_type": "TestReport"}
{"nodeid": "test_report_example.py::test_ok", "location": ["test_report_example.py", 0, "test_ok"], "keywords": {"test_ok": 1, "pytest-reportlog": 1, "test_report_example.py": 1}, "outcome": "passed", "longrepr": null, "when": "teardown", "user_properties": [], "sections": [], "duration": 0.00099945068359375, "$report_type": "TestReport"}
{"nodeid": "test_report_example.py::test_fail", "location": ["test_report_example.py", 4, "test_fail"], "keywords": {"test_fail": 1, "pytest-reportlog": 1, "test_report_example.py": 1}, "outcome": "passed", "longrepr": null, "when": "setup", "user_properties": [], "sections": [], "duration": 0.0, "$report_type": "TestReport"}
{"nodeid": "test_report_example.py::test_fail", "location": ["test_report_example.py", 4, "test_fail"], "keywords": {"test_fail": 1, "pytest-reportlog": 1, "test_report_example.py": 1}, "outcome": "failed", "longrepr": {"reprcrash": {"path": "D:\\projects\\pytest-reportlog\\test_report_example.py", "lineno": 6, "message": "assert (4 + 4) == 1"}, "reprtraceback": {"reprentries": [{"type": "ReprEntry", "data": {"lines": ["    def test_fail():", ">       assert 4 + 4 == 1", "E       assert (4 + 4) == 1"], "reprfuncargs": {"args": []}, "reprlocals": null, "reprfileloc": {"path": "test_report_example.py", "lineno": 6, "message": "AssertionError"}, "style": "long"}}], "extraline": null, "style": "long"}, "sections": [], "chain": [[{"reprentries": [{"type": "ReprEntry", "data": {"lines": ["    def test_fail():", ">       assert 4 + 4 == 1", "E       assert (4 + 4) == 1"], "reprfuncargs": {"args": []}, "reprlocals": null, "reprfileloc": {"path": "test_report_example.py", "lineno": 6, "message": "AssertionError"}, "style": "long"}}], "extraline": null, "style": "long"}, {"path": "D:\\projects\\pytest-reportlog\\test_report_example.py", "lineno": 6, "message": "assert (4 + 4) == 1"}, null]]}, "when": "call", "user_properties": [], "sections": [], "duration": 0.0009992122650146484, "$report_type": "TestReport"}
{"nodeid": "test_report_example.py::test_fail", "location": ["test_report_example.py", 4, "test_fail"], "keywords": {"test_fail": 1, "pytest-reportlog": 1, "test_report_example.py": 1}, "outcome": "passed", "longrepr": null, "when": "teardown", "user_properties": [], "sections": [], "duration": 0.0, "$report_type": "TestReport"}
{"exitstatus": 1, "$report_type": "SessionFinish"}""")

        test_report = TestingReport.from_run("", log)

        self.assertFalse(test_report.success)

        expected_failed = {'test_report_example.py::test_fail'}
        self.assertEqual(expected_failed, test_report.failed_tests)
