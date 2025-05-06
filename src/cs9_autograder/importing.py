from contextlib import contextmanager, redirect_stdout
from dataclasses import dataclass
from enum import auto, Enum
import importlib.util
import os
from pathlib import Path
import sys
from types import ModuleType
from typing import cast, Optional

_DEFAULT_SUBMISSION_PATH = Path('/autograder/submission')
_SUBMISSION_PATH: Optional[Path] = None


@dataclass(frozen=True)
class FailedImport:
    filename: str
    err: Exception

    # if true, then the file appears to be missing.
    # if false, the import failed for another reason
    missing: bool


# We need to keep track of failed imports because the call to `import_student`
# is not usually inised of a TestCase.
# Autograder will then report the failures when its test methods are run.
FAILED_IMPORTS: set[FailedImport] = set()


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


def import_student(module_name: str) -> Optional[ModuleType]:
    with ignore_prints():
        module_filename = (module_name + '.py')

        path = submission_path() / module_filename
        try:
            return import_from_file(path, module_name)

        except FileNotFoundError as err:
            missing = module_name in str(err)
            FAILED_IMPORTS.add(FailedImport(module_filename, err, missing))
            return None

        except Exception as err:
            FAILED_IMPORTS.add(FailedImport(module_filename, err, False))
            return None


def import_from_file(path: Path | str, module_name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None:
        raise TypeError(f'Unable to create spec from `{path}`')

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module

    spec.loader.exec_module(module)  # type: ignore
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
