import json
import os
import pathlib
import pytest
import shutil
import sys
import traceback
import yaml
from pathlib import Path
from selenium.webdriver.firefox.webdriver import WebDriver as WebDriverFirefox
from . import logger


# Counter used for image files naming
count = 0
img_width = "300px"
img_height = "200px"
description_tag = "h2"


#
# Auxiliary functions and classes
#
def check_browser_option(browser):
    if browser is None:
        msg = "The usage of 'webdriver' fixture requires the pytest-selenium-auto plugin.\n'--browser' option is missing.\n"
        print(msg, file=sys.stderr)
        sys.exit(pytest.ExitCode.USAGE_ERROR)


def check_html_option(htmlpath):
    if htmlpath is None:
        msg = "It seems you are using pytest-selenium-auto plugin.\npytest-html plugin is required.\n'--html' option is missing.\n"
        print(msg, file=sys.stderr)
        sys.exit(pytest.ExitCode.USAGE_ERROR)


def getini(config, name):
    """ Workaround for bug https://github.com/pytest-dev/pytest/issues/11282 """
    value = config.getini(name)
    if not isinstance(value, str):
        value = None
    return value


def create_assets(folder_report, driver_config):
    """ Recreate screenshots and log folders and files """
    # Recreate screenshots_folder
    folder = ""
    if folder_report is not None and folder_report != '':
        folder = f"{folder_report}{os.sep}"
    # Create Screenshots folders
    shutil.rmtree(f"{folder}screenshots", ignore_errors=True)
    pathlib.Path(f"{folder}screenshots").mkdir(parents=True)
    # Save error.png in screenshots folder
    resources_path = Path(__file__).parent.joinpath("resources")
    error_img = Path(resources_path, "error.png")
    shutil.copy(str(error_img), f"{folder}screenshots")
    # Copy config file
    if driver_config is not None and folder != "":
        shutil.copy(driver_config, f"{folder}{driver_config}")
    # Recreate logs folder and file
    logger.init()


def load_json_yaml_file(filename):
    """
    Load the file into a dictionary.
    If the file is invalid, return empty dictionary.
    """
    if filename is not None:
        if filename.endswith('.json'):
            try:
                f = open(filename)
                data = json.load(f)
                f.close()
                return data
            except Exception as e:
                trace = traceback.format_exc()
                logger.append_driver_error(f"Error loading '{filename}' file. Your JSON file will be ignored", str(e), trace)
                return {}
        elif filename.endswith('.yaml') or filename.endswith('.yml'):
            try:
                f = open(filename)
                data = yaml.safe_load(f)
                f.close()
                return data
            except Exception as e:
                trace = traceback.format_exc()
                logger.append_driver_error(f"Error loading '{filename}' file. Your YAML file will be ignored", str(e), trace)
                return {}
    else:
        return {}


def counter():
    """ Returns a counter used for image file naming """
    global count
    count += 1
    return count


def save_screenshot(driver, folder_report):
    """ Save the image in the specifie folder and return the filename """
    index = counter()
    linkname = f"screenshots{os.sep}image-{index}.png"
    folder = ""
    if folder_report is not None and folder_report != '':
        folder = f"{folder_report}{os.sep}"
    filename = folder + linkname
    try:
        if isinstance(driver, WebDriverFirefox):
            driver.save_full_page_screenshot(filename)
        else:
            driver.save_screenshot(filename)
    except Exception as e:
        trace = traceback.format_exc()
        linkname = f"screenshots{os.sep}error.png"
        print(f"{str(e)}\n\n{trace}", file=sys.stderr)
    finally:
        return linkname


#
# Auxiliary functions for the report generation
#
def append_header(call, report, extra, pytest_html, description):
    # Append description
    if description is not None:
        description = description.strip().replace('\n', '<br>')
        extra.append(pytest_html.extras.html(f"<{description_tag}>{description}</{description_tag}>"))

    # Append exception
    exception_logged = False
    # Catch explicit pytest.fail and pytest.skip calls
    if hasattr(call, 'excinfo') \
            and call.excinfo is not None \
            and call.excinfo.typename in ('Failed','Skipped') \
            and hasattr(call.excinfo, "value") \
            and hasattr(call.excinfo.value, "msg"):
        extra.append(pytest_html.extras.html(f"<pre><span style='color:black;'>{call.excinfo.typename}</span> reason = {call.excinfo.value.msg}</pre>"))
        exception_logged = True
    # Catch XFailed tests
    if report.skipped and hasattr(report, 'wasxfail'):
        extra.append(pytest_html.extras.html(f"<pre><span style='color:black;'>XFailed</span> reason = {report.wasxfail}</pre>"))
        exception_logged = True
    # Catch XPassed tests
    if report.passed and hasattr(report, 'wasxfail'):
        extra.append(pytest_html.extras.html(f"<pre><span style='color:black;'>XPassed</span> reason = {report.wasxfail}</pre>"))
        exception_logged = True
    # Catch explicit pytest.xfail calls and runtime exceptions in failed tests
    if hasattr(call, 'excinfo') \
            and call.excinfo is not None \
            and call.excinfo.typename not in ('Failed', 'Skipped')\
            and hasattr(call.excinfo, '_excinfo') \
            and call.excinfo._excinfo is not None \
            and isinstance(call.excinfo._excinfo, tuple) and len(call.excinfo._excinfo) > 1:
        extra.append(pytest_html.extras.html(f"<pre><span style='color:black;'>{call.excinfo.typename}</span> {call.excinfo._excinfo[1]}</pre>"))
        exception_logged = True
    # extra.append(pytest_html.extras.html("<br>"))
    return exception_logged


def get_anchor_tag(image, div=True):
    style = f"border: 1px solid black;"
    if div:
        style += " width: 300px; float: right;"
        anchor = f"<a href=\"{image}\" target=\"_blank\"><img src =\"{image}\" style=\"{style}\"></a>"
        return "<div class=\"image\">" + anchor + "</div>"
    else:
        style += f" width: {img_width};"
        anchor = f"<a href=\"{image}\" target=\"_blank\"><img src =\"{image}\" style=\"{style}\"></a>"
        return anchor


def append_image(extra, pytest_html, item, linkname):
    if "WARNING" in linkname:
        extra.append(pytest_html.extras.html(f"<pre style='color:red;'>{linkname}</pre>"))
        logger.append_screenshot_error(item.location[0], item.location[2])
    else:
        extra.append(pytest_html.extras.html(f"<img src ='{linkname}'>"))

