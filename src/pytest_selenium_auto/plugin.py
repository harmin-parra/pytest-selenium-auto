import importlib
import os
import pytest
import traceback
from importlib.metadata import version
from pytest_metadata.plugin import metadata_key
from selenium.webdriver.support.events import EventFiringWebDriver
from selenium.webdriver.firefox.webdriver import WebDriver as WebDriverFirefox
from selenium.webdriver.chrome.webdriver import WebDriver as WebDriverChrome
from selenium.webdriver.edge.webdriver import WebDriver as WebDriverEdge
from selenium.webdriver.safari.webdriver import WebDriver as WebDriverSafari

from . import (
    logger,
    utils,
)
from .event_listener import CustomEventListener


#
# Definition of test parameters
#
def pytest_addoption(parser):
    group = parser.getgroup("pytest-selenium-auto")
    group.addoption(
        "--browser",
        action="store",
        default=None,
        help="The driver to use.",
        choices=("firefox", "chrome", "edge", "safari"),
    )
    group.addoption(
        "--screenshots",
        action="store",
        default="all",
        help="The screenshot gathering strategy.",
        choices=("all", "last", "failed", "none"),
    )

    parser.addini(
        "maximize_window",
        type="bool",
        default=False,
        help="Whether to maximize the browser window",
    )
    parser.addini(
        "description_tag",
        type="string",
        default="h2",
        help="HTML tag for test descriptions. Choices={h1, h2, h3, p, pre}",
    )
    parser.addini(
        "separator_display",
        type="bool",
        default=True,
        help="Whether to separate screenshots by a horizontal line",
    )
    parser.addini(
        "separator_color",
        type="string",
        default="gray",
        help="The color of the horizontal line",
    )
    parser.addini(
        "separator_height",
        type="string",
        default="5px",
        help="The height of the horizontal line",
    )


#
# Read test parameters
#

@pytest.fixture(scope='session')
def browser(request):
    _browser = request.config.getoption("--browser")
    utils.check_browser_option(_browser)
    return _browser

@pytest.fixture(scope='session')
def screenshots(request):
    return request.config.getoption("--screenshots")

@pytest.fixture(scope='session')
def folder_report(request):
    folder = request.config.getoption("--html")
    utils.check_html_option(folder)
    folder = os.path.dirname(request.config.getoption("--html"))
    utils.recreate_assets(folder)
    return folder

@pytest.fixture(scope='session')
def maximize_window(request):
    return request.config.getini("maximize_window")

@pytest.fixture(scope='session')
def description_tag(request):
    tag = request.config.getini("description_tag")
    if tag in ("h1", "h2", "h3", "p", "pre"):
        return tag
    else:
        return 'h2'

@pytest.fixture(scope='session')
def separator_display(request):
    return request.config.getini("separator_display")

@pytest.fixture(scope='session')
def separator_color(request):
    return request.config.getini("separator_color")

@pytest.fixture(scope='session')
def separator_height(request):
    return request.config.getini("separator_height")

@pytest.fixture(scope="session")
def dump_options(request, browser, screenshots, maximize_window):
    logger.dump_options(browser, screenshots, maximize_window)


#
# Test fixtures
#

@pytest.fixture(scope='function')
def images(request, screenshots):
    return []


@pytest.fixture(scope='function')
def webdriver(request, browser, images, maximize_window,
              folder_report, screenshots, dump_options):

    # Lets deal with the driver
    driver = None
    try:
        if browser == "firefox":
            driver = WebDriverFirefox()
        elif browser == "chrome":
            driver = WebDriverChrome()
        elif browser == "edge":
            driver = WebDriverEdge()
        elif browser == "safari":
            driver = WebDriverSafari()
    except Exception as e:
        trace = traceback.format_exc()
        logger.append_driver_error(f"Error creating '{browser}' driver", str(e), trace)
        if driver is not None:
            try:
                driver.quit()
            except Exception as e:
                pass
        raise

    setattr(driver, 'images', images)
    setattr(driver, 'screenshots', screenshots)
    setattr(driver, 'folder_report', folder_report)

    if maximize_window:
        driver.maximize_window()

    event_listener = CustomEventListener()
    wrapped_driver = EventFiringWebDriver(driver, event_listener)

    yield wrapped_driver

    wrapped_driver.quit()


#
# Hookers
#

passed  = 0
failed  = 0
xfailed = 0
skipped = 0
xpassed = 0
errors  = 0

#
# Modify the exit code
#
def pytest_sessionfinish(session, exitstatus):
    summary = []
    if failed > 0:
        summary.append(str(failed) + " failed")
    if passed > 0:
        summary.append(str(passed) + " passed")
    if skipped > 0:
        summary.append(str(skipped) + " skipped")
    if xfailed > 0:
        summary.append(str(xfailed) + " xfailed")
    if xpassed > 0:
        summary.append(str(xpassed) + " xpassed")
    if errors > 0:
        summary.append(str(errors) + " errors")
    print('\nSummary: ' + ', '.join(summary))

    if exitstatus == 0:
        if xfailed > 0 or xpassed > 0:
            session.exitstatus = 6
        else:
            session.exitstatus = 0
    else:
        session.exitstatus = exitstatus

#
# Override pytest-html report generation
#
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    pytest_html = item.config.pluginmanager.getplugin('html')
    outcome = yield
    report = outcome.get_result()
    extra = getattr(report, 'extra', [])

    # Let's deal with the HTML report
    if report.when == 'call':
        # Get function/method description
        pkg = item.location[0].replace(os.sep, '.')[:-3]
        index = pkg.rfind('.')
        module = importlib.import_module(package = pkg[:index], name = pkg[index + 1:])
        # Is the called test a function ?
        if item.location[2].find('.') == -1:
            func = getattr(module, item.location[2])
        # Is the called test a class method ?
        else:
            index = item.location[2].find('.')
            cls = getattr(module, item.location[2][:index])
            func = getattr(cls, item.location[2][index + 1:])
        description = getattr(func, '__doc__')

        try:
            feature_request = item.funcargs['request']
        except Exception as e:
            return
        # Is this plugin running?
        try:
            browser = feature_request.getfixturevalue('browser')
        except pytest.FixtureLookupError as e:
            return
        # Get test fixture values
        screenshots = feature_request.getfixturevalue('screenshots')
        driver = feature_request.getfixturevalue('webdriver')
        images = feature_request.getfixturevalue('images')
        description_tag = feature_request.getfixturevalue("description_tag")
        separator_display = feature_request.getfixturevalue("separator_display")
        separator_color = feature_request.getfixturevalue("separator_color")
        separator_height = feature_request.getfixturevalue("separator_height")

        utils.append_description(call, report, extra, pytest_html, description, description_tag, screenshots)

        if screenshots == "none":
            report.extra = extra
            return

        if description is not None and separator_display:
            extra.append(pytest_html.extras.html(f"<hr style='height:{separator_height};background-color:{separator_color}'>"))
        if screenshots == 'all':
            for img in images:
                utils.append_image(extra, pytest_html, item, img)
                if separator_display:
                    extra.append(pytest_html.extras.html(f"<hr style='height:{separator_height};background-color:{separator_color}'>"))
                else:
                    extra.append(pytest_html.extras.html("<br>"))
        else:
            images = []
            xfail = hasattr(report, 'wasxfail')
            if screenshots == "last" or xfail or report.outcome in ('failed', 'skipped'):
                utils.save_screenshot(driver, images, driver.folder_report)
                utils.append_image(extra, pytest_html, item, images[0])

        report.extra = extra

    # Let's deal with exit status
    global skipped, failed, xfailed, passed, xpassed, errors

    if call.when == 'call':
        if report.failed:
            failed += 1
        if report.skipped and not hasattr(report, "wasxfail"):
            skipped += 1
        if report.skipped and hasattr(report, "wasxfail"):
            xfailed += 1
        if report.passed and hasattr(report, "wasxfail"):
            xpassed += 1
        if report.passed and not hasattr(report, "wasxfail"):
            passed += 1

    if call.when == 'setup':
        # For tests with the pytest.mark.skip fixture
        if report.skipped and hasattr(call, 'excinfo') and call.excinfo is not None and call.excinfo.typename == 'Skipped':
            skipped += 1
        # For setup fixture
        if report.failed and call.excinfo is not None:
            errors += 1

    # For teardown fixture
    if call.when == 'teardown':
        if report.failed and call.excinfo is not None:
            errors += 1


#
# Add some info to the metadata
#
@pytest.hookimpl(trylast=True)
def pytest_configure(config):
    metadata = config.pluginmanager.getplugin("metadata")
    if metadata:
        try:
            metadata = config._metadata
        except AttributeError:
            metadata = config.stash[metadata_key]
    try:
        browser = config.getoption("browser")
        maximize_window = config.getini("maximize_window")
        folder_report = os.path.dirname(config.getoption("htmlpath"))
        metadata['Browser'] = browser.capitalize()
        try:
            metadata['Selenium'] = version("selenium")
        except Exception as e:
            metadata['Selenium'] = "not installed"
    except Exception as e:
        pass
    finally:
        config._metadata = metadata
