import traceback
import unittest

from .formatting import h_rule, quoted_listing
from .importing import FAILED_IMPORTS

class Autograder(unittest.TestCase):
    def test_student_imports(self):
        """Check if there have been any failed imports, and report them to the
        student"""
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
