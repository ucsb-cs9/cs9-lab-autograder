from io import StringIO
from contextlib import redirect_stdout
import os
from pathlib import Path
from typing import Optional

import unittest
from unittest import TestCase

from cs9_autograder import (Autograder, ignore_prints, importing, import_student,
                            set_submission_path, submission_path)

from .mixins import (SubmissionPathRestorer, TestTester, restore_submission_path_config,
                    get_submission_path_config)


class TestSubmissionPath(SubmissionPathRestorer, TestCase):
    def test_submission_path_default(self):
        actual = submission_path()
        expected = Path('/autograder/submission')
        self.assertEqual(expected, actual)

    def test_submission_path_env(self):
        my_path = Path('/my/custom/path')
        os.environ['SUBMISSION_PATH'] = str(my_path)

        self.assertEqual(my_path, submission_path())

    def test_set_submission_path(self):
        my_path = Path('/some/other/path')
        set_submission_path(my_path)

        self.assertEqual(my_path, submission_path())

    def test_set_submission_path_overrides_env(self):
        os.environ['SUBMISSION_PATH'] = '/env/path'
        my_path = Path('/override/path')
        set_submission_path(my_path)

        self.assertEqual(my_path, submission_path())


class TestImportStudent(TestTester, SubmissionPathRestorer, TestCase):
    def setUp(self):
        super().setUp()

        script_dir = Path(__file__).resolve().parent
        self.test_path = script_dir / 'importing_test_files'
        set_submission_path(self.test_path)

    def tearDown(self):
        super().tearDown()

        importing.FAILED_IMPORTS.clear()

    def test_import_student_working(self):
        student_mod = import_student('working')

        self.assertTrue(student_mod.hello_world())

    def test_import_student_file_not_exist(self):
        student_mod = import_student('non_existant')

        class Grader(Autograder):
            pass

        # we should get one failure from Autograder's test_student_imports
        self.assertTestCaseFailure(Grader)

    def test_import_student_exception_during_import(self):
        student_mod = import_student('value_error')

        class Grader(Autograder):
            pass

        # we should get one failure from Autograder's test_student_imports
        self.assertTestCaseFailure(Grader)


class TestIgnorePrints(TestCase):
    def test_ignore_prints(self):
        with redirect_stdout(StringIO()) as f:
            with ignore_prints():
                print("hello world!")
        self.assertFalse(f.getvalue())


class TestModuleToPath(TestCase):
    pass
