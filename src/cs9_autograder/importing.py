from contextlib import contextmanager, redirect_stdout
from dataclasses import dataclass
from enum import auto, Enum
import importlib.util
import importlib.machinery
from modulefinder import ModuleFinder
import os
import os.path
from pathlib import Path
import sys
from types import ModuleType
from typing import cast, Optional
import uuid
import warnings

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


@contextmanager
def student_import(import_path: Optional[Path | str] = None,
                   mangle: bool = True):
    if import_path is None:
        import_path = submission_path()

    with prepend_import_path(import_path, mangle=mangle):
        with ignore_prints():
            try:
                yield None
            except ModuleNotFoundError as err:
                mod_name = err.name
                print(f'Could not import module {mod_name}. '
                      f'Did you name your file correctly and include it in '
                      'your submission?')
                raise err


@contextmanager
def prepend_import_path(import_path: Path | str, mangle: bool = True):
    original_modules = set(sys.modules)

    import_path = str(import_path)
    import_path = os.path.realpath(import_path, strict=True)
    try:
        sys.path.insert(1, import_path)
        yield None
    finally:
        if sys.path[1] == import_path:
            del sys.path[1]
        else:
            warnings.warn(f'Did not delete `{import_path}` from sys.path '
                          'because it was no longer at index 1.',
                          RuntimeWarning)

        if mangle:
            # assume all new items in sys.modules should get mangled
            new_modules = set(sys.modules) - original_modules
            for mod in new_modules:
                mangle_module(mod)


def mangle_module(module: str, suffix: Optional[str] = None):
    """Mangle a module in sys.modules.
    This is needed if you need to import two modules with the same name
    (for example, importing a student and correct module with the
    same name.)

    see: https://stackoverflow.com/a/76316559"""

    if not suffix:
        suffix = uuid.uuid1().hex

    mangled = f'__{module}_{suffix}__'
    sys.modules[mangled] = sys.modules[module]
    del sys.modules[module]






def import_from_file(path: Path | str, module_name: str) -> ModuleType:
    # This seems to have a side effect in adding path to the global module search path?
    # Not sure what the issue is.

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


def imported_modules(module_name: str, search_path: Path | str) -> set[str]:
    """Return the names of all modules imported by a script."""

    finder = ModuleFinder(path=[str(search_path)])
    module_path = module_to_path(module_name, search_path)
    finder.run_script(str(module_path))

    modules = set(finder.modules.keys())
    modules.remove('__main__')

    return modules


def module_to_path(module_name: str, search_path: Path | str) -> Path:
    """Get the absolute path of a module.
    module_name: The fully qualified name of the module
    path: the path in which to search for the module"""

    path = [str(search_path)]  # PathFinder doesn't support `Path`s yet.
    spec = importlib.machinery.PathFinder.find_spec(module_name, path)
    if not spec:
        raise ModuleNotFoundError("Could not find loader for module "
                                  f'`{module_name}` in path `{search_path}`.')

    if not spec.origin:
        # this case may occur if the
        raise ModuleNotFoundError(f'The spec for `{module_name}` has no'
                                  ' origin.')

    try:
        module_path = Path(spec.origin).resolve(strict=True)
    except OSError:
        raise ModuleNotFoundError(f'The module path `{module_path}` does not '
                                  'exist.')

    return module_path


def path_to_module(module_file: Path | str, search_path: Path | str) -> str:
    """Convert from a path to a module name

    module_file: the path to the python module
    search_path: the where the module can be found. For a single-file python
    script, this is the script file's directory."""

    module_file = Path(module_file)
    search_path = Path(search_path)

    if module_file.suffix != '.py':
        raise ValueError(f'module_file `{module_file}` is not a .py file. '
                         '(packages are not yet supported in path_to_module.)')

    if module_file.is_absolute():
        module_file = module_file.relative_to(search_path)

    if len(module_file.parts) != 1:
        raise NotImplementedError("Module name resolution is not yet supported"
                                  "for packages. "
                                  f'`{module_file}`')

    return str(module_file.with_suffix(''))
