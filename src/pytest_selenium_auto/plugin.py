import importlib
import os
import pytest
import re
from importlib.metadata import version
from pytest_metadata.plugin import metadata_key
from selenium.webdriver.support.events import EventFiringWebDriver

from . import utils
from .browser_settings import (
    browser_options,
    browser_service,
)
from .configuration_loader import set_driver_capabilities
from .webdrivers import (
    CustomEventListener,
    WebDriver_Firefox,
    WebDriver_Chrome,
    WebDriver_Chromium,
    WebDriver_Edge,
    WebDriver_Safari,
)


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
        choices=("firefox", "chrome", "chromium", "edge", "safari"),
    )
    group.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="Whether to run the browser in headless mode.",
    )
    group.addoption(
        "--screenshots",
        action="store",
        default="all",
        help="The screenshot gathering strategy.",
        choices=("all", "last", "failed", "manual", "none"),
    )
    parser.addini(
        "maximize_window",
        type="bool",
        default=False,
        help="Whether to maximize the browser window.",
    )
    parser.addini(
        "driver_firefox",
        type="string",
        default=None,
        help="Firefox driver path.",
    )
    parser.addini(
        "driver_chrome",
        type="string",
        default=None,
        help="Chrome driver path.",
    )
    parser.addini(
        "driver_chromium",
        type="string",
        default=None,
        help="Chromium driver path.",
    )
    parser.addini(
        "driver_edge",
        type="string",
        default=None,
        help="Edge driver path.",
    )
    parser.addini(
        "driver_safari",
        type="string",
        default=None,
        help="Safari driver path.",
    )
    parser.addini(
        "driver_config",
        type="string",
        default=None,
        help="driver json or yaml configuration file path.",
    )
    parser.addini(
        "description_tag",
        type="string",
        default="h2",
        help="HTML tag for the test description. Choices={h1, h2, h3, p, pre}",
    )
    parser.addini(
        "separator_display",
        type="bool",
        default=False,
        help="Whether to separate screenshots by a horizontal line.",
    )
    parser.addini(
        "separator_color",
        type="string",
        default="gray",
        help="The color of the horizontal line.",
    )
    parser.addini(
        "separator_height",
        type="string",
        default="5px",
        help="The height of the horizontal line.",
    )
    parser.addini(
        "thumbnail_width",
        type="string",
        default="300px",
        help="The width of the screenshot thumbnail.",
    )
    parser.addini(
        "thumbnail_height",
        type="string",
        default="200px",
        help="The height of the screenshot thumbnail.",
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
def headless(request):
    return request.config.getoption("--headless")

@pytest.fixture(scope='session')
def folder_report(request):
    folder = request.config.getoption("--html")
    utils.check_html_option(folder)
    folder = os.path.dirname(request.config.getoption("--html"))
    return folder

@pytest.fixture(scope='session')
def description_tag(request):
    tag = request.config.getini("description_tag")
    if tag in ("h1", "h2", "h3", "p", "pre"):
        return tag
    else:
        return 'h2'

@pytest.fixture(scope='session')
def maximize_window(request):
    return request.config.getini("maximize_window")

@pytest.fixture(scope='session')
def separator_display(request):
    return request.config.getini("separator_display")

@pytest.fixture(scope='session')
def separator_color(request):
    return request.config.getini("separator_color")

@pytest.fixture(scope='session')
def separator_height(request):
    return request.config.getini("separator_height")

@pytest.fixture(scope='session')
def thumbnail_width(request):
    return request.config.getini("thumbnail_width")

@pytest.fixture(scope='session')
def driver_firefox(request):
    return utils.getini(request.config, "driver_firefox")

@pytest.fixture(scope='session')
def driver_chrome(request):
    return utils.getini(request.config, "driver_chrome")

@pytest.fixture(scope='session')
def driver_chromium(request):
    return utils.getini(request.config, "driver_chromium")

@pytest.fixture(scope='session')
def driver_edge(request):
    return utils.getini(request.config, "driver_edge")

@pytest.fixture(scope='session')
def driver_safari(request):
    return utils.getini(request.config, "driver_safari")

@pytest.fixture(scope='session')
def driver_config(request):
    return utils.getini(request.config, "driver_config")

@pytest.fixture(scope="session")
def config_data(request, driver_config):
    return utils.load_json_yaml_file(driver_config)

@pytest.fixture(scope='session')
def driver_paths(request, driver_firefox, driver_chrome, driver_chromium, driver_edge, driver_safari):
    """ Return a dictionary containing user-provided web driver paths """
    return {
        'firefox':  driver_firefox,
        'chrome':   driver_chrome,
        'chromium': driver_chromium,
        'edge':     driver_edge,
        'safari':   driver_safari,
        }


@pytest.fixture(scope='session')
def check_options(request, browser, driver_config, folder_report, description_tag, thumbnail_width):
    utils.img_width = thumbnail_width
    utils.description_tag = description_tag
    utils.check_browser_option(browser)
    utils.create_assets(folder_report, driver_config)


#
# Test fixtures
#

@pytest.fixture(scope='function')
def images(request):
    return []


@pytest.fixture(scope='function')
def _driver(request, check_options, browser, folder_report,
            maximize_window, images, screenshots,
            config_data, browser_options, browser_service):
    """ Instantiates the webdriver """
    driver = None
    try:
        if browser == "firefox":
            driver = WebDriver_Firefox(options=browser_options, service=browser_service)
        elif browser == "chrome":
            driver = WebDriver_Chrome(options=browser_options, service=browser_service)
        elif browser == "chromium":
            driver = WebDriver_Chromium(options=browser_options, service=browser_service)
        elif browser == "edge":
            driver = WebDriver_Edge(options=browser_options, service=browser_service)
        elif browser == "safari":
            driver = WebDriver_Safari(options=browser_options, service=browser_service)
    except:
        if driver is not None:
            try:
                driver.quit()
            except:
                pass
        raise

    driver.images = images
    driver.screenshots = screenshots
    driver.folder_report = folder_report
    try:
        set_driver_capabilities(driver, browser, config_data)
    except:
        if driver is not None:
            try :
                driver.quit()
            except:
                pass
        raise
    if maximize_window:
        driver.maximize_window()

    event_listener = CustomEventListener()
    wrapped_driver = EventFiringWebDriver(driver, event_listener)

    yield wrapped_driver

    wrapped_driver.quit()


@pytest.fixture(scope='function')
def webdriver(_driver):
    yield _driver


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
        match_cls = re.search(r"^[^\[]*\.", item.location[2])
        if match_cls is None:
            func = getattr(module, item.originalname)
        else:
            cls = getattr(module, match_cls[0][:-1])
            func = getattr(cls, item.originalname)
        description = getattr(func, '__doc__')

        try:
            feature_request = item.funcargs['request']
        except:
            return
        # Is this plugin required/being used?
        try:
            browser = feature_request.getfixturevalue('browser')
        except pytest.FixtureLookupError:
            return
        # Get test fixture values
        screenshots = feature_request.getfixturevalue('screenshots')
        driver = feature_request.getfixturevalue('webdriver')
        images = feature_request.getfixturevalue('images')
        description_tag = feature_request.getfixturevalue("description_tag")
        separator_display = feature_request.getfixturevalue("separator_display")
        separator_color = feature_request.getfixturevalue("separator_color")
        separator_height = feature_request.getfixturevalue("separator_height")

        exception_logged = utils.append_header(call, report, extra, pytest_html, description)

        if screenshots == "none":
            report.extra = extra
            return

        if (description is not None or exception_logged is True) \
                and separator_display is True \
                and screenshots in ('all', 'manual'):
            extra.append(pytest_html.extras.html(f"<hr style='height:{separator_height};background-color:{separator_color}'>"))

        anchors = ""
        if screenshots in ('all', 'manual'):
            for image in images:
                anchors += utils.get_anchor_tag(image, div=False)
        elif screenshots == "last":
            image = utils.save_screenshot(driver, driver.folder_report)
            extra.append(pytest_html.extras.html(utils.get_anchor_tag(image)))
        if screenshots in ("failed", "manual"):
            xfail = hasattr(report, 'wasxfail')
            if xfail or report.outcome in ('failed', 'skipped'):
                image = utils.save_screenshot(driver, driver.folder_report)
                if screenshots == "manual":
                    anchors += utils.get_anchor_tag(image, div=False)
                else:
                    extra.append(pytest_html.extras.html(utils.get_anchor_tag(image)))
        if anchors != "":
            extra.append(pytest_html.extras.html(anchors))

        report.extra = extra
        #logger.append_screenshot_error(item.location[0], item.location[2])

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
        headless = config.getoption("headless")
        screenshots = config.getoption("screenshots")
        folder_report = os.path.dirname(config.getoption("htmlpath"))
        driver_config = utils.getini(config, "driver_config")
        metadata['Browser'] = browser.capitalize()
        metadata['Headless'] = str(headless).lower()
        metadata['Screenshots'] = screenshots
        try:
            metadata['Selenium'] = version("selenium")
        except:
            metadata['Selenium'] = "unknown"
        if driver_config is not None and os.path.isfile(driver_config):
            if utils.load_json_yaml_file(driver_config) != {}:
                metadata["Driver configuration"] = f"<a href='{driver_config}'>{driver_config}</a><span style=\"color:green;\"> (valid)</span>"
            else:
                metadata["Driver configuration"] = f"<a href='{driver_config}'>{driver_config}</a><span style=\"color:red;\"> (invalid)</span>"
    except:
        pass
    finally:
        config._metadata = metadata
