from io import StringIO
from contextlib import redirect_stdout
import os
from pathlib import Path
from typing import Optional

import unittest
from unittest import TestCase

from cs9_autograder import ignore_prints, import_student, set_submission_path, submission_path


class TestSubmissionPath(TestCase):
    def setUp(self):
        self.path_config = get_submission_path_config()

    def tearDown(self):
        restore_submission_path_config(self.path_config)

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

class TestImportStudent(TestCase):
    def setUp(self):
        self.path_config = get_submission_path_config()

        script_dir = Path(os.path.dirname(os.path.realpath(__file__)))
        self.test_path = script_dir / 'importing_test_files'
        set_submission_path(self.test_path)

    def tearDown(self):
        restore_submission_path_config(self.path_config)

    def test_import_student_working(self):
        student_mod = import_student('working')

        print(student_mod)

        self.assertTrue(student_mod.hello_world())


class TestIgnorePrints(TestCase):
    def test_ignore_prints(self):
        with redirect_stdout(StringIO()) as f:
            with ignore_prints():
                print("hello world!")
        self.assertFalse(f.getvalue())


SubmissionPathConfig = tuple[Optional[Path], Optional[str]]

def get_submission_path_config() -> SubmissionPathConfig:
    from cs9_autograder import importing

    global_path = importing._SUBMISSION_PATH
    try:
        env_path = os.environ['SUBMISSION_PATH']
    except KeyError:
        env_path = None

    return global_path, env_path


def restore_submission_path_config(config: SubmissionPathConfig):
    from cs9_autograder import importing

    global_path, env_path = config
    importing._SUBMISSION_PATH = global_path

    if env_path is None:
        try:
            del os.environ['SUBMISSION_PATH']
        except KeyError:
            pass
    else:
        os.environ['SUBMISSION_PATH'] = env_path
