import json
import os
import pathlib
import pytest
import shutil
import sys
import traceback
import yaml
from . import logger


# Counter used for image files naming
count = 0


#
# Auxiliary functions to check options
#
def check_browser_option(browser):
    if browser is None:
        msg = ("The usage of 'webdriver' fixture requires the pytest-selenium-auto plugin.\n"
               "'--browser' option is missing.\n")
        print(msg, file=sys.stderr)
        sys.exit(pytest.ExitCode.USAGE_ERROR)


def check_html_option(htmlpath):
    if htmlpath is None:
        msg = ("It seems you are using pytest-selenium-auto plugin.\n"
               "pytest-html plugin is required.\n"
               "'--html' option is missing.\n")
        print(msg, file=sys.stderr)
        sys.exit(pytest.ExitCode.USAGE_ERROR)


def getini(config, name):
    """ Workaround for bug https://github.com/pytest-dev/pytest/issues/11282 """
    value = config.getini(name)
    if not isinstance(value, str):
        value = None
    return value


def check_options(browser, report_folder):
    check_html_option(report_folder)
    check_browser_option(browser)


def create_assets(report_folder, driver_config):
    """ Recreate screenshots, page sources and log folders and files """
    # Recreate screenshots_folder
    folder = ""
    if report_folder is not None and report_folder != '':
        folder = f"{report_folder}{os.sep}"
    # Create page sources folder
    shutil.rmtree(f"{folder}sources", ignore_errors=True)
    pathlib.Path(f"{folder}sources").mkdir(parents=True)
    # Create screenshots folder
    shutil.rmtree(f"{folder}screenshots", ignore_errors=True)
    pathlib.Path(f"{folder}screenshots").mkdir(parents=True)
    # Copy error.png to screenshots folder
    resources_path = pathlib.Path(__file__).parent.joinpath("resources")
    error_img = pathlib.Path(resources_path, "error.png")
    shutil.copy(str(error_img), f"{folder}screenshots")
    # Copy config file to report folder
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
                logger.append_driver_error(f"Error loading '{filename}' file. Your JSON file will be ignored",
                                           str(e), trace)
                return {}
        elif filename.endswith('.yaml') or filename.endswith('.yml'):
            try:
                f = open(filename)
                data = yaml.safe_load(f)
                f.close()
                return data
            except Exception as e:
                trace = traceback.format_exc()
                logger.append_driver_error(f"Error loading '{filename}' file. Your YAML file will be ignored",
                                           str(e), trace)
                return {}
    else:
        return {}


def counter():
    """ Returns a counter used for image and page source file naming """
    global count
    count += 1
    return count


def save_resources(driver, report_folder):
    index = counter()
    image = save_screenshot(driver, report_folder, index)
    source = None
    if driver.log_page_source:
        source = save_page_source(driver, report_folder, index)
    return image, source


def save_screenshot(driver, report_folder, index):
    """ Save the image in the specified folder and return the filename for the anchor link """
    link = f"screenshots{os.sep}image-{index}.png"
    folder = ""
    if report_folder is not None and report_folder != '':
        folder = f"{report_folder}{os.sep}"
    filename = folder + link
    try:
        if hasattr(driver, "save_full_page_screenshot"):
            driver.save_full_page_screenshot(filename)
        else:
            driver.save_screenshot(filename)
    except Exception as e:
        trace = traceback.format_exc()
        link = f"screenshots{os.sep}error.png"
        print(f"{str(e)}\n\n{trace}", file=sys.stderr)
    finally:
        return link


def save_page_source(driver, report_folder, index):
    """ Save the page source in the specified folder and return the filename for the anchor link """
    link = f"sources{os.sep}page-{index}.txt"
    folder = ""
    if report_folder is not None and report_folder != '':
        folder = f"{report_folder}{os.sep}"
    filename = folder + link
    try:
        source = driver.page_source
        f = open(filename, 'w')
        f.write(source)
        f.close()
    except Exception as e:
        trace = traceback.format_exc()
        link = None
        print(f"{str(e)}\n\n{trace}", file=sys.stderr)
    finally:
        return link


#
# Auxiliary functions for the report generation
#
def append_header(call, report, extra, pytest_html,
                  description, description_tag):
    """ Append description and exception trace """
    # Append description
    if description is not None:
        description = escape_html(description).strip().replace('\n', '<br>')
        extra.append(pytest_html.extras.html(f"<{description_tag}>{description}</{description_tag}>"))

    # Append exception
    exception_logged = False
    # Catch explicit pytest.fail and pytest.skip calls
    if (
        hasattr(call, 'excinfo') and
        call.excinfo is not None and
        call.excinfo.typename in ('Failed', 'Skipped') and
        hasattr(call.excinfo, "value") and
        hasattr(call.excinfo.value, "msg")
    ):
        extra.append(pytest_html.extras.html(
            "<pre>"
            f"<span style='color:black;'>{escape_html(call.excinfo.typename)}</span>"
            f" reason = {escape_html(call.excinfo.value.msg)}"
            "</pre>"
            )
        )
        exception_logged = True
    # Catch XFailed tests
    if report.skipped and hasattr(report, 'wasxfail'):
        extra.append(pytest_html.extras.html(
            "<pre>"
            "<span style='color:black;'>XFailed</span>"
            f" reason = {escape_html(report.wasxfail)}"
            "</pre>"
            )
        )
        exception_logged = True
    # Catch XPassed tests
    if report.passed and hasattr(report, 'wasxfail'):
        extra.append(pytest_html.extras.html(
            "<pre>"
            "<span style='color:black;'>XPassed</span>"
            f" reason = {escape_html(report.wasxfail)}"
            "</pre>"
            )
        )
        exception_logged = True
    # Catch explicit pytest.xfail calls and runtime exceptions in failed tests
    if (
        hasattr(call, 'excinfo') and
        call.excinfo is not None and
        call.excinfo.typename not in ('Failed', 'Skipped') and
        hasattr(call.excinfo, '_excinfo') and
        call.excinfo._excinfo is not None and
        isinstance(call.excinfo._excinfo, tuple) and
        len(call.excinfo._excinfo) > 1
    ):
        extra.append(pytest_html.extras.html(
            "<pre>"
            f"<span style='color:black;'>{escape_html(call.excinfo.typename)}</span>"
            f" {escape_html(call.excinfo._excinfo[1])}"
            "</pre>"
            )
        )
        exception_logged = True
    # extra.append(pytest_html.extras.html("<br>"))
    return exception_logged


def escape_html(msg):
    return str(msg).replace('<', '&lt;').replace('>', '&gt;')


def get_anchor_tag(image):
    anchor = decorate_href(image, "selenium_log_img")
    return anchor


def get_anchor_tags(image, source):
    image = decorate_href(image, "selenium_log_img")
    if source is not None:
        source = decorate_page_source(source)
        return f"<div class=\"selenium_div\">{image}<br>{source}</div>"
    else:
        return image


def get_table_row_tag(comment, image, source, clazz="selenium_log_comment"):
    """ Return HTML table row with event label and screenshot anchor link """
    image = decorate_href(image, "selenium_log_img")
    if type(comment) == dict:
        comment = decorate_description(comment)
    elif type(comment) == str:
        comment = decorate_label(comment, clazz)
    else:
        comment = ""
    if source is not None:
        source = decorate_page_source(source, clazz)
        return (
            f"<tr><td>{comment}</td><td class=\"selenium_td\">"
            f"<div class=\"selenium_td_div\">{image}<br>{source}</div></td></tr>"
        )
    else:
        return f"<tr><td>{comment}</td><td class=\"selenium_td\"><div class=\"selenium_td_div\">{image}</div></td></tr>"


def decorate_description(description):
    if description is None:
        return ""

    if 'comment' not in description:
        description['comment'] = None
    if 'url' not in description:
        description['url'] = None
    if 'value' not in description:
        description['value'] = None
    if 'locator' not in description:
        description['locator'] = None
    if 'attributes' not in description:
        description['attributes'] = None

    if description['comment'] is not None:
        return decorate_label(description['comment'], "selenium_log_comment")
    label = decorate_label(description['action'], "selenium_log_action")
    if description['url'] is not None:
        label += " " + decorate_label(description['url'], "selenium_log_target")
    else:
        if description['value'] is not None:
            label += " " + decorate_quotation() + description['value'] + decorate_quotation()
        if description['locator'] is not None or description['attributes'] is not None:
            label += "<br/><br>"
            if description['locator'] is not None:
                locator = description['locator'].replace('"', decorate_quotation())
                label += "Locator: " + decorate_label(locator, "selenium_log_target") + "<br/><br>"
            if description['attributes'] is not None:
                label += "Attributes: " + decorate_label(description['attributes'], "selenium_log_target")
    return decorate_label(label, "selenium_log_description")


def decorate_label(label, clazz):
    return f"<span class=\"{clazz}\">{label}</span>"


def decorate_href(link, clazz):
    return f"<a href=\"{link}\" target=\"_blank\"><img src =\"{link}\" class=\"{clazz}\"></a>"


def decorate_page_source(filename, clazz=""):
    return f"<a href=\"{filename}\" target=\"_blank\">[page source]</a>"


def decorate_quotation():
    return decorate_label("\"", "quotation")


#
# Function decorators to handle exceptions.
#
def try_catch_wrap_event(message):
    """ Wrapper to handle exceptions during webdriver events logging. """
    def decorator(func):
        def wrapped(*args, **kwargs):
            try:
                response = func(*args, **kwargs)
            except Exception as e:
                e = str(e)
                trace = traceback.format_exc()
                msg = f"{e}\n\n{trace}"
                print(msg, file=sys.stderr)
                response = decorate_label(message, "selenium_log_fatal")
            return response
        return wrapped
    return decorator


def try_catch_wrap_driver(message):
    """ Wrapper to handle exceptions during webdriver instantiation. """
    def decorator(func):
        def wrapped(*args, **kwargs):
            try:
                response = func(*args, **kwargs)
            except Exception as e:
                trace = traceback.format_exc()
                logger.append_driver_error(message, e, trace)
                raise e
            return response
        return wrapped
    return decorator


def check_lists_length(report, item, list1, *lists):
    message = ("Lists \"images\", \"comments\" and/or \"sources\" don't have the same length. "
               "Screenshots won't be logged for this test.")
    size = len(list1)
    for listx in lists:
        if size != len(listx):
            log_error_message(report, item, message)
            return False
    return True


def log_error_message(report, item, message):
    report.sections.append(("pytest-selenium-auto log", message))
    logger.append_report_error(item.location[0], item.location[2], message)


def get_folder(filepath):
    folder = None
    if filepath is not None:
        folder = os.path.dirname(filepath)
    return folder
