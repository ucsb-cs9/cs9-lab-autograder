from contextlib import contextmanager, redirect_stdout
import os

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
