from io import StringIO
from contextlib import redirect_stdout

import unittest
from unittest import TestCase

from cs9_autograder import ignore_prints

class TestIgnorePrints(TestCase):
    def test_ignore_prints(self):
        with redirect_stdout(StringIO()) as f:
            with ignore_prints():
                print("hello world!")
        self.assertFalse(f.getvalue())
