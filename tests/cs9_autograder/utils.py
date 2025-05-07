import os
from pathlib import Path
from typing import Optional
import unittest

from cs9_autograder import importing


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


SubmissionPathConfig = tuple[Optional[Path], Optional[str]]


def get_submission_path_config() -> SubmissionPathConfig:
    """Save the student submission path so we can restore it later."""
    global_path = importing._SUBMISSION_PATH
    try:
        env_path = os.environ['SUBMISSION_PATH']
    except KeyError:
        env_path = None

    return global_path, env_path


def restore_submission_path_config(config: SubmissionPathConfig):
    global_path, env_path = config
    importing._SUBMISSION_PATH = global_path

    if env_path is None:
        try:
            del os.environ['SUBMISSION_PATH']
        except KeyError:
            pass
    else:
        os.environ['SUBMISSION_PATH'] = env_path
