from contextlib import contextmanager, redirect_stdout
import importlib.util
import os
from pathlib import Path
import sys
from types import ModuleType

_DEFAULT_SUBMISSION_PATH = Path('/autograder/submission')
_SUBMISSION_PATH = None

def submission_path() -> Path:
    """Returns the student submission path.

    The student submission path will be searched for in the following way:
    - Use the _SUBMISSION_PATH global variable if it is not none
    - Use the SUBMISSION_PATH OS environment variable if it is set
    - Otherwise, use the default submission path `/autograder/submission`
    """
    if _SUBMISSION_PATH:
        return _SUBMISSION_PATH

    try:
        return Path(os.environ['SUBMISSION_PATH'])
    except KeyError:
        pass

    return _DEFAULT_SUBMISSION_PATH


def set_submission_path(submission_path: Path | str) -> None:
    global _SUBMISSION_PATH
    _SUBMISSION_PATH = Path(submission_path)


def import_student(module_name: str) -> ModuleType:
    path = submission_path() / (module_name + '.py')
    return import_from_file(path, module_name)


def import_from_file(path: Path | str, module_name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module




class ignore_prints:
    """A context manager that prevents print statements from outputting to stdout
    """

    def __init__(self):
        self.dev_null = open(os.devnull, 'w')
        self.redirect_stdout = redirect_stdout(self.dev_null)

    def __enter__(self):
        self.dev_null.__enter__()
        self.redirect_stdout.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        redirect_exit = self.redirect_stdout.__exit__(exc_type, exc_value, traceback)
        dev_null_exit = self.dev_null.__exit__(exc_type, exc_value, traceback)
        return redirect_exit or dev_null_exit
