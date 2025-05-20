from io import StringIO
from contextlib import redirect_stdout
import copy
import os
from pathlib import Path
import sys
from typing import Optional

import unittest
from unittest import TestCase

from cs9_autograder import (Autograder, ignore_prints, importing,                             imported_modules,
                            module_to_path, path_to_module,
                            prepend_import_path,
                            set_submission_path, student_import, submission_path)

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


class TestStudentImport(TestTester, SubmissionPathRestorer, TestCase):
    def setUp(self):
        super().setUp()

        script_dir = Path(__file__).resolve().parent
        self.test_path = script_dir / 'importing_test_files'
        set_submission_path(self.test_path)

    def tearDown(self):
        super().tearDown()

        importing.FAILED_IMPORTS.clear()

    def test_student_import_no_caching(self):
        """Outside of the student_import context manager, we shouldn't be able
        to import the student module."""
        with student_import():
            import working

        with self.assertRaises(ImportError):
            import working as working_1

    def test_student_import_working(self):
        with student_import():
            import working
        self.assertTrue(working.hello_world())

    def test_student_import_file_not_exist(self):
        with student_import():
            with self.assertRaises(ImportError):
                import non_existant

    def test_studen_import_exception_during_import(self):
        with student_import():
            with self.assertRaises(AttributeError):
                import value_error


class TestIgnorePrints(TestCase):
    def test_ignore_prints(self):
        with redirect_stdout(StringIO()) as f:
            with ignore_prints():
                print("hello world!")
        self.assertFalse(f.getvalue())


class TestImportedModules(TestCase):
    def search_path(self):
        script_dir = Path(__file__).resolve().parent
        return script_dir / 'imported_modules_test_files'

    def test_imported_modules(self):
        search_path = self.search_path()

        actual = imported_modules('testFile', search_path)
        expected = {'from_import_as', 'from_import', 'import_as', 'imported'}

        self.assertEqual(expected, actual)


class TestModuleToPath(TestCase):
    def search_path(self):
        script_dir = Path(__file__).resolve().parent
        return script_dir / 'module_to_path_test_files'

    def test_module_to_path(self):
        search_path = self.search_path()

        actual = module_to_path('my_module', search_path)
        expected = search_path / 'my_module.py'
        self.assertEqual(expected, actual)


class TestPathToModule(TestCase):
    def search_path(self):
        script_dir = Path(__file__).resolve().parent
        return script_dir / 'module_to_path_test_files'

    def test_path_to_module(self):
        search_path = self.search_path()

        actual = path_to_module(search_path / 'my_module.py', search_path)
        expected = 'my_module'
        self.assertEqual(expected, actual)


class PrependImportPath(TestCase):
    def base_path(self):
        script_dir = Path(__file__).resolve().parent
        return script_dir / 'prepend_import_path_test_files'

    def test_prepend_import_path(self):
        original_path = copy.copy(sys.path)

        with prepend_import_path(self.base_path() / 'good'):
            import good_module

        self.assertTrue(good_module.good_function)
        self.assertListEqual(original_path, sys.path)

    def test_prepend_import_path_mangle(self):
        original_path = copy.copy(sys.path)

        # mangle=True should be the default.
        with prepend_import_path(self.base_path() / 'good'):
            from good_module import good_function as good_good
        with prepend_import_path(self.base_path() / 'different'):
            from good_module import good_function as different_good

        self.assertIsNot(good_good, different_good)
