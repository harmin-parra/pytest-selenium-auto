import os
import pathlib
import shutil
import sys
import traceback


logfile = f"logs{os.sep}webdriver.log"
separator = 64 * '='


def init():
    """ Recreate logs folder and file """
    # Delete existing logs folder and file, if any
    shutil.rmtree("logs", ignore_errors=True)
    pathlib.Path("logs").mkdir()
    '''
    # Create log file
    try:
        pathlib.Path(f"{logfile}").unlink(missing_ok=True)
        open(logfile, 'w').close()
    except Exception as e:
        trace = traceback.format_exc()
        print(f"Error creating '{logfile}' file\n", file=sys.stderr)
        print(f"{str(e)}\n\n{trace}\n", file=sys.stderr)
    '''


def append_driver_error(description, error=None, traceback=None):
    content = description
    if error is not None:
        content = content + '\n\n' + str(error)
    if traceback is not None:
        content = content + '\n\n' + traceback
    print(content, file=sys.stderr)
    content += f"\n{separator}\n\n"
    _write(content)


def append_report_error(module, function, message):
    _write(f"{module} :: {function}  -  {message}\n")


def _write(content):
    try:
        f = open(logfile, 'a')
        f.write(content)
        f.close()
    except Exception as e:
        trace = traceback.format_exc()
        print(f"Error writing to '{logfile}' file\n", file=sys.stderr)
        print(f"{str(e)}\n\n{trace}\n", file=sys.stderr)
