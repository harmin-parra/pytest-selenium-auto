import os
import pathlib
import pytest
import shutil
import sys
import traceback
from selenium.webdriver.firefox.webdriver import WebDriver as WebDriverFirefox
from . import logger


# Counter used for image files naming
count = 0

#
# Auxiliary functions and classes
#
def check_browser_option(browser):
    if browser is None:
        msg = "The usage of 'webdriver' fixture requires the pytest-selenium-auto plugin.\n'--browser' option is missing.\n"
        #logger.append_driver_error(msg)
        print(msg, file=sys.stderr)
        sys.exit(pytest.ExitCode.USAGE_ERROR)


def check_html_option(htmlpath):
    if htmlpath is None:
        msg = "It seems you are using pytest-selenium-auto plugin.\npytest-html plugin is required.\n'--html' option is missing.\n"
        #logger.append_driver_error(msg)
        print(msg, file=sys.stderr)
        sys.exit(pytest.ExitCode.USAGE_ERROR)


# Workaround for bug https://github.com/pytest-dev/pytest/issues/11282
def getini(config, name):
    value = config.getini(name)
    if not isinstance(value, str):
        value = None
    return value


def recreate_assets(folder_report):
    # Recreate screenshots_folder
    if folder_report is not None and folder_report != '':
        shutil.rmtree(f"{folder_report}{os.sep}screenshots", ignore_errors=True)
        pathlib.Path(f"{folder_report}{os.sep}screenshots").mkdir(parents=True)
    else:
        shutil.rmtree("screenshots", ignore_errors=True)
        pathlib.Path("screenshots").mkdir()
    # Recreate Logs folder and file
    logger.init()


# returns a counter used for image file naming
def counter():
    global count
    count += 1
    return count


def save_screenshot(driver, images, folder_report):
    if images is not None:
        index = counter()
        linkname = f"screenshots{os.sep}image-{index}.png"
        if folder_report is not None and folder_report != '':
            filename = f"{folder_report}{os.sep}screenshots{os.sep}image-{index}.png"
        else:
            filename = linkname
        try:
            if isinstance(driver, WebDriverFirefox):
                driver.save_full_page_screenshot(f"{filename}")
            else:
                driver.save_screenshot(f"{filename}")
        except Exception as e:
            trace = traceback.format_exc()
            linkname = "WARNING: Failed to gather screenshot"
            print(f"{str(e)}\n\n{trace}", file=sys.stderr)
        finally:
            images.append(f"{linkname}")


#
# Auxiliary functions for the report generation
#
def append_description(call, report, extra, pytest_html,
                       description, description_tag, screenshots):
    if description is not None:
        description = description.strip().replace('\n', '<br>')
        if not (screenshots == "failure" and report.passed is True and not hasattr(report, "wasxfail")):
            extra.append(pytest_html.extras.html(f"<{description_tag}>{description}</{description_tag}>"))
    # Catch explicit pytest.fail and pytest.skip calls
    if hasattr(call, 'excinfo') and call.excinfo is not None and (call.excinfo.typename == 'Failed' or call.excinfo.typename == 'Skipped'):
        extra.append(pytest_html.extras.html(f"<pre><span style='color:black;'>{call.excinfo.typename}</span> reason = {call.excinfo.value.msg}</pre>"))
    # Catch XFailed tests
    if report.skipped and hasattr(report, 'wasxfail'):
        extra.append(pytest_html.extras.html(f"<pre><span style='color:black;'>XFailed</span> reason = {report.wasxfail}</pre>"))
    # Catch XPassed tests
    if report.passed and hasattr(report, 'wasxfail'):
        extra.append(pytest_html.extras.html(f"<pre><span style='color:black;'>XPassed</span> reason = {report.wasxfail}</pre>"))
    # Catch exceptions in failed tests
    if hasattr(call, 'excinfo') and call.excinfo is not None and call.excinfo.typename not in ('Failed', 'Skipped'):
        if hasattr(call.excinfo, '_excinfo') and call.excinfo._excinfo is not None \
        and isinstance(call.excinfo._excinfo, tuple) and len(call.excinfo._excinfo) > 1:
            extra.append(pytest_html.extras.html(f"<pre><span style='color:black;'>{call.excinfo.typename}</span> {call.excinfo._excinfo[1]}</pre>"))
    #extra.append(pytest_html.extras.html("<br>"))


def append_image(extra, pytest_html, item, linkname):
    if "WARNING" in linkname:
        extra.append(pytest_html.extras.html(f"<pre style='color:red;'>{linkname}</pre>"))
        logger.append_screenshot_error
        logger.append_screenshot_error(item.location[0], item.location[2])
    else:
        extra.append(pytest_html.extras.html(f"<img src ='{linkname}'>"))
