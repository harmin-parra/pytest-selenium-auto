import importlib
import os
import pathlib
import pytest
import re
from importlib.metadata import version
from pytest_metadata.plugin import metadata_key
from selenium.webdriver.firefox.webdriver import WebDriver as WebDriver_Firefox
from selenium.webdriver.chrome.webdriver import WebDriver as WebDriver_Chrome
from selenium.webdriver.chromium.webdriver import ChromiumDriver as WebDriver_Chromium
from selenium.webdriver.edge.webdriver import WebDriver as WebDriver_Edge
from selenium.webdriver.safari.webdriver import WebDriver as WebDriver_Safari

from . import (
    markers,
    supported_browsers,
    utils
)
from .browser_settings import (
    browser_options,
    browser_service,
)
from .configuration_loader import set_driver_capabilities
from .listener import CustomEventListener
from .wrappers import (
    CustomEventFiringWebDriver,
    wrap_driver,
)


#
# Definition of test options
#
def pytest_addoption(parser):
    group = parser.getgroup("pytest-selenium-auto")
    group.addoption(
        "--browser",
        action="store",
        default=None,
        help="The driver to use.",
        choices=supported_browsers,
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
    group.addoption(
        "--log-attributes",
        action="store_true",
        default=False,
        help="Whether to log WebElement attributes. Only applicable when --screenshots=all",
    )
    group.addoption(
        "--log-page-source",
        action="store_true",
        default=False,
        help="Whether to log page sources.",
    )
    group.addoption(
        "--log-verbose",
        action="store_true",
        default=False,
        help="Whether to log WebElement attributes and web page sources.",
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
        help="HTML tag for the test description. Accepted values: h1, h2, h3, p or pre.",
    )
    parser.addini(
        "pause",
        type="string",
        default="0",
        help="Number of seconds to pause after webdriver events."
    )


#
# Read test parameters
#
@pytest.fixture(scope='session')
def browser(request):
    return request.config.getoption("--browser")


@pytest.fixture(scope='session')
def screenshots(request):
    return request.config.getoption("--screenshots")


@pytest.fixture(scope='session')
def headless(request):
    return request.config.getoption("--headless")


@pytest.fixture(scope='session')
def verbose(request):
    return request.config.getoption("--log-verbose")


@pytest.fixture(scope='session')
def log_attributes(request):
    return request.config.getoption("--log-attributes")


@pytest.fixture(scope='session')
def log_page_source(request):
    return request.config.getoption("--log-page-source")


@pytest.fixture(scope='session')
def report_folder(request):
    htmlpath = request.config.getoption("--html")
    return utils.get_folder(htmlpath)


@pytest.fixture(scope='session')
def report_css(request):
    return request.config.getoption("--css")


@pytest.fixture(scope='session')
def description_tag(request):
    tag = request.config.getini("description_tag")
    return tag if tag in ("h1", "h2", "h3", "p", "pre") else "h2"


@pytest.fixture(scope='session')
def maximize_window(request):
    return request.config.getini("maximize_window")


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


@pytest.fixture(scope='session')
def pause(request):
    try:
        return float(utils.getini(request.config, "pause"))
    except ValueError:
        return 0


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
def check_options(request, browser, report_folder, driver_config):
    utils.check_browser_option(browser)
    utils.create_assets(report_folder, driver_config)


#
# Test fixtures
#
@pytest.fixture(scope='function')
def images(request):
    return []


@pytest.fixture(scope='function')
def sources(request):
    return []


@pytest.fixture(scope='function')
def comments(request):
    return []


@pytest.fixture(scope='function')
def _driver(request, browser, report_folder, config_data, driver_config, driver_paths,
            images, sources, comments, screenshots, pause, headless, maximize_window,
            check_options, verbose, log_attributes, log_page_source):

    log_attributes = log_attributes or verbose
    log_page_source = log_page_source or verbose

    # Update settings from markers
    marker_window = markers.get_marker_window(request.node)
    config_data.update({'window': marker_window})

    marker_screenshots = markers.get_marker_screenshots(request.node)
    if marker_screenshots is not None:
        screenshots = marker_screenshots

    marker_browser = markers.get_marker_browser(request.node)
    if marker_browser is not None:
        browser = marker_browser

    marker_log_attributes = markers.get_marker_log_attributes(request.node)
    if marker_log_attributes is True:
        log_attributes = marker_log_attributes

    marker_log_page_source = markers.get_marker_log_page_source(request.node)
    if marker_log_page_source is True:
        log_page_source = marker_log_page_source

    marker_log_verbose = markers.get_marker_log_verbose(request.node)
    if marker_log_verbose is True:
        log_attributes = marker_log_verbose
        log_page_source = marker_log_verbose

    # Instantiate webdriver
    driver = None
    opt = browser_options(browser, config_data, headless)
    srv = browser_service(browser, config_data, driver_paths)
    try:
        if browser == "firefox":
            driver = WebDriver_Firefox(options=opt, service=srv)
        elif browser == "chrome":
            driver = WebDriver_Chrome(options=opt, service=srv)
        elif browser == "chromium":
            driver = WebDriver_Chromium(browser_name="Chromium", vendor_prefix="Chromium", options=opt, service=srv)
        elif browser == "edge":
            driver = WebDriver_Edge(options=opt, service=srv)
        elif browser == "safari":
            driver = WebDriver_Safari(options=opt, service=srv)
    except:
        if driver is not None:
            try:
                driver.quit()
            except:
                pass
        raise

    # Set driver metadata
    wrap_driver(driver, screenshots, images, sources, comments, report_folder, log_attributes, log_page_source)

    # Set capabilities
    set_driver_capabilities(driver, browser, config_data)

    # Set window
    if (
        (maximize_window is True and 'maximize' not in marker_window)
        or
        ('maximize' in marker_window and marker_window['maximize'] is True)
    ):
        driver.maximize_window()
    if 'minimize' in marker_window and marker_window['minimize'] is True:
        driver.minimize_window()
    if 'fullscreen' in marker_window and marker_window['fullscreen'] is True:
        driver.fullscreen_window()

    # Set pause
    marker_pause = markers.get_marker_pause(request.node)
    if marker_pause is not None:
        pause = marker_pause

    # Decorate driver
    event_listener = CustomEventListener(pause)
    wrapped_driver = CustomEventFiringWebDriver(driver, event_listener)

    yield wrapped_driver

    wrapped_driver.quit()


@pytest.fixture(scope='function')
def webdriver(_driver):
    yield _driver


#
# Hookers
#
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """ Override report generation. """
    pytest_html = item.config.pluginmanager.getplugin('html')
    outcome = yield
    report = outcome.get_result()
    extras = getattr(report, 'extras', [])

    if not ("request" in item.funcargs and "browser" in item.funcargs):
        return

    # Let's deal with the HTML report
    if report.when == 'call':
        # Get function/method description
        pkg = item.location[0].replace(os.sep, '.')[:-3]
        index = pkg.rfind('.')
        module = importlib.import_module(package=pkg[:index], name=pkg[index + 1:])
        # Is the called test a function ?
        match_cls = re.search(r"^[^\[]*\.", item.location[2])
        if match_cls is None:
            func = getattr(module, item.originalname)
        else:
            cls = getattr(module, match_cls[0][:-1])
            func = getattr(cls, item.originalname)
        description = getattr(func, "__doc__")

        # Is the test item using the 'browser' fixtures?
        if not ("request" in item.funcargs and "browser" in item.funcargs):
            return
        feature_request = item.funcargs['request']

        # Get test fixture values
        driver = feature_request.getfixturevalue("webdriver")
        images = feature_request.getfixturevalue("images")
        sources = feature_request.getfixturevalue("sources")
        comments = feature_request.getfixturevalue("comments")
        description_tag = feature_request.getfixturevalue("description_tag")
        screenshots = driver.screenshots
        log_attributes = driver.log_attributes
        #log_page_source = driver.log_page_source

        # Append test description and execution exception trace, if any.
        utils.append_header(call, report, extras, pytest_html, description, description_tag)

        if screenshots == "none":
            return

        if not utils.check_lists_length(report, item, driver):
            return

        # Generate HTML code for the extras to be added in the report
        links = ""  # Used when logging without comments
        rows = ""   # Used when logging with comments
        if screenshots == "all" and not log_attributes:
            #if log_page_source:
                for i in range(len(images)):
                    links += utils.decorate_anchors(images[i], sources[i])
            #else:
            #    for img in images:
            #        extras.append(pytest_html.extras.png(img))
        elif (
            screenshots == "manual"
            or (screenshots == "all" and log_attributes)
        ):
            for i in range(len(images)):
                rows += utils.get_table_row_tag(comments[i], images[i], sources[i])
        elif screenshots == "last":
            resources = utils.save_resources(driver, driver.report_folder)
            #if log_page_source:
            links = utils.decorate_anchors(resources[0], resources[1])
            #else:
            #    extras.append(pytest_html.extras.png(resources[0]))
        if screenshots in ("failed", "manual"):
            xfail = hasattr(report, 'wasxfail')
            if xfail or report.outcome in ("failed", "skipped"):
                resources = utils.save_resources(driver, driver.report_folder)
                if screenshots == "manual":
                    if xfail or report.outcome == "failed":
                        event = "failure"
                    else:
                        event = "skip"
                    rows += utils.get_table_row_tag(
                                f"Last screenshot before {event}",
                                resources[0], resources[1],
                                clazz="selenium_log_description"
                            )
                else:
                    #if log_page_source:
                        links = utils.decorate_anchors(resources[0], resources[1])
                    #else:
                    #    extras.append(pytest_html.extras.png(resources[0]))

        # Add horizontal line between the header and the comments/screenshots
        if len(extras) > 0 and len(links) + len(rows) > 0:
            extras.append(pytest_html.extras.html(f'<hr class="selenium_separator">'))

        # Append extras
        if links != "":
            extras.append(pytest_html.extras.html(links))
        if rows != "":
            rows = (
                '<table style="width: 100%;">'
                + rows +
                "</table>"
            )
            extras.append(pytest_html.extras.html(rows))
        report.extras = extras

        # Check if there was a screenshot gathering failure
        if screenshots != 'none':
            for image in images:
                if image == f"screenshots{os.sep}error.png":
                    message = "Failed to gather screenshot(s)"
                    utils.log_error_message(report, item, message)
                    break


@pytest.hookimpl(trylast=False)
def pytest_configure(config):
    # Register custom markers
    config.addinivalue_line("markers", "browser(arg)")
    config.addinivalue_line("markers", "pause(arg)")
    config.addinivalue_line("markers", "window(kwargs)")
    config.addinivalue_line("markers", "screenshots(arg)")
    config.addinivalue_line("markers", "log_verbose")
    config.addinivalue_line("markers", "log_attributes")
    config.addinivalue_line("markers", "log_page_source")

    # Add metadata
    metadata = config.pluginmanager.getplugin("metadata")
    if metadata:
        metadata = config.stash[metadata_key]
        try:
            # Get request options to add to metadata
            browser = config.getoption("browser")
            pause = utils.getini(config, "pause")
            headless = config.getoption("headless")
            screenshots = config.getoption("screenshots")
            driver_config = utils.getini(config, "driver_config")
            metadata['Browser'] = browser.capitalize()
            metadata['Headless'] = str(headless).lower()
            metadata['Screenshots'] = screenshots
            metadata['Pause'] = pause + " second(s)"
            metadata['Selenium'] = version("selenium")
            if driver_config is not None and os.path.isfile(driver_config):
                if utils.load_json_yaml_file(driver_config) != {}:
                    metadata["Driver configuration"] = (
                        f'<a href="{driver_config}">{driver_config}</a>'
                        f'<span style="color:green;"> (valid)</span>'
                    )
                else:
                    metadata["Driver configuration"] = (
                        f'<a href="{driver_config}">{driver_config}</a>'
                        f'<span style="color:red;"> (invalid)</span>'
                    )
        except Exception:
            pass

    # Add CSS file to --css request option for pytest-html
    # This code doesn't always run before pytest-html configuration
    report_css = config.getoption("--css")
    resources_path = pathlib.Path(__file__).parent.joinpath("resources")
    style_css = pathlib.Path(resources_path, "style.css")
    report_css.insert(0, style_css)


'''
def pytest_terminal_summary(terminalreporter, exitstatus, config):
    for item in terminalreporter.stats.items():
        passed = []
        failed = []
        xpassed = []
        xfailed = []
        skipped = []
        if item[0] == "passed":
            passed = item[1]
        if item[0] == "failed":
            failed = item[1]
        if item[0] == "skipped":
            skipped = item[1]
        if item[0] == "xpassed":
            xpassed = item[1]
        if item[0] == "xfailed":
            xfailed = item[1]
'''
