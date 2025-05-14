from .autograder import Autograder
from .differential import (d_compare, d_returned, d_method)
from .importing import (ignore_prints, import_from_file, import_student,
                        imported_modules,
                        module_to_path, path_to_module,
                        set_submission_path,
                        submission_path)
from .testing import (t_coverage, t_module, TestingReport)


# from the gradescope autograder
class weight(object):
    """Simple decorator to add a __weight__ property to a function

    Usage: @weight(3.0)
    """
    def __init__(self, val):
        self.val = val

    def __call__(self, func):
        func.__weight__ = self.val
        return func
