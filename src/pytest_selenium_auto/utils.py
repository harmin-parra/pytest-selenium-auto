import json
import os
import pathlib
import pytest
import shutil
import sys
import traceback
import yaml
from pathlib import Path
from . import logger


# Counter used for image files naming
count = 0


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


def create_assets(report_folder, report_css, driver_config):
    """ Recreate screenshots and log folders and files """
    # Recreate screenshots_folder
    folder = ""
    if report_folder is not None and report_folder != '':
        folder = f"{report_folder}{os.sep}"
    # Create screenshots folders
    shutil.rmtree(f"{folder}screenshots", ignore_errors=True)
    pathlib.Path(f"{folder}screenshots").mkdir(parents=True)
    # Copy error.png to screenshots folder
    resources_path = Path(__file__).parent.joinpath("resources")
    error_img = Path(resources_path, "error.png")
    shutil.copy(str(error_img), f"{folder}screenshots")
    # Add custom CSS file to pytest-html --css option
    style_css = Path(resources_path, "style.css")
    report_css.insert(0, style_css)
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


def save_screenshot(driver, report_folder):
    """ Save the image in the specified folder and return the filename for the anchor link """
    index = counter()
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


#
# Auxiliary functions for the report generation
#
def append_header(call, report, extra, pytest_html,
                  description, description_tag):
    """ Append description and exception trace """
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
    if div:
        anchor = decorate_href(image, "selenium_extras_img")
        return "<div class=\"image\">" + anchor + "</div>"
    else:
        anchor = decorate_href(image, "selenium_log_img")
        return anchor


def get_table_row_tag(comment, image, clazz="selenium_log_comment"):
    """ Return HTML table row with event label and screenshot anchor link """
    link = decorate_href(image, "selenium_log_img")
    if type(comment) == dict:
        comment = decorate_description(comment)
    if type(comment) == str:
        comment = decorate_label(comment, clazz)
    if comment is None:
        comment = ""
    return f"<tr><td>{comment}</td><td class=\"selenium_td_img\"><div class=\"selenium_div_img\">{link}</div></td></tr>"


def append_image(extra, pytest_html, item, linkname):
    if "WARNING" in linkname:
        extra.append(pytest_html.extras.html(f"<pre style='color:red;'>{linkname}</pre>"))
        logger.append_screenshot_error(item.location[0], item.location[2])
    else:
        extra.append(pytest_html.extras.html(f"<img src ='{linkname}'>"))


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
            label += " " + decorate_quotation() + description['value'] + decorate_quotation() + " to"
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

def decorate_quotation():
    return decorate_label("\"", "quotation")
