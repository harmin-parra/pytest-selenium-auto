import os
import pathlib
import shutil
import sys
import traceback


logfile = f"logs{os.sep}webdriver.log"
separator = "================================================================"


def init():
    # Delete existing logs folder, if any
    shutil.rmtree("logs", ignore_errors=True)
    pathlib.Path("logs").mkdir()
    # Create logs folder and file
    try:
        pathlib.Path(f"{logfile}").unlink(missing_ok=True)
        open(logfile, 'w').close()
    except Exception as e:
        trace = traceback.format_exc()
        print(f"Error creating '{logfile}' file\n", file=sys.stderr)
        print(f"{str(e)}\n\n{trace}\n", file=sys.stderr)


def dump_options(browser, screenshots, maximize_window):
    msg = f"Options :\n\n"
    msg += f"browser = {browser}\n"
    msg += f"screenshots = {screenshots}\n"
    msg += f"maximize_window = {maximize_window}\n\n"
    msg += f"{separator}\n\n"
    _write(msg)


def append_driver_error(description, error=None, traceback=None):
    content = description
    if error is not None:
        content = content + '\n\n' + error
    if traceback is not None:
        content = content + '\n\n' + traceback
    print(content, file=sys.stderr)
    content += f"\n{separator}\n\n"
    _write(content)


def append_screenshot_error(module, function):
    _write(f"{module} :: {function}  -  Failed to gather screenshot\n")


def _write(content):
    try:
        f = open(logfile, 'a')
        f.write(content)
        f.close()
    except Exception as e:
        trace = traceback.format_exc()
        print(f"Error writing to '{logfile}' file\n", file=sys.stderr)
        print(f"{str(e)}\n\n{trace}\n", file=sys.stderr)
