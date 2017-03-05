import contextlib
import sys
from io import StringIO

@contextlib.contextmanager
def silenced(no_stdout=True, no_stderr=True):
    """
    Suppresses output to stdout and/or stderr.
    Always resets stdout and stderr, even on an exception.
    Usage:
        with silenced(): print("This doesn't print")
    Modified from post by Alex Martelli in https://stackoverflow.com/questions/2828953/silence-the-stdout-of-a-function-in-python-without-trashing-sys-stdout-and-resto/2829036#2829036
    which is licensed under CC BY-SA 3.0 https://creativecommons.org/licenses/by-sa/3.0/
    """
    if no_stdout:
        save_stdout = sys.stdout
        sys.stdout = StringIO()
    if no_stderr:
        save_stderr = sys.stderr
        sys.stderr = StringIO()
    yield
    if no_stdout:
        sys.stdout = save_stdout
    if no_stderr:
        sys.stderr = save_stderr