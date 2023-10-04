import importlib
import os
import pytest
import re
from importlib.metadata import version
from pytest_metadata.plugin import metadata_key
from selenium.webdriver.support.events import EventFiringWebDriver

from . import (
    logger,
    markers,
    supported_browsers,
    utils
)
from .browser_settings import (
    browser_options,
    browser_service,
)
from .configuration_loader import set_driver_capabilities
from .webdrivers import (
    CustomEventListener,
    WebDriverFirefox,
    WebDriverChrome,
    WebDriverChromium,
    WebDriverEdge,
    WebDriverSafari,
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
        "--show-attributes",
        action="store_true",
        default=False,
        help="Whether to log WebElement attributes. Only applicable when --screenshots=all",
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
def verbose(request):
    return request.config.getoption("--show-attributes")


@pytest.fixture(scope='session')
def report_folder(request):
    folder = request.config.getoption("--html")
    utils.check_html_option(folder)
    folder = os.path.dirname(request.config.getoption("--html"))
    return folder


@pytest.fixture(scope='session')
def report_css(request):
    return request.config.getoption("--css")


@pytest.fixture(scope='session')
def description_tag(request):
    tag = request.config.getini("description_tag")
    return tag if tag in ("h1", "h2", "h3", "p", "pre") else 'h2'


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
    except:
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
def check_options(request, browser, report_folder, report_css, driver_config):
    utils.check_browser_option(browser)
    utils.create_assets(report_folder, report_css, driver_config)


#
# Test fixtures
#
@pytest.fixture(scope='function')
def images(request):
    return []


@pytest.fixture(scope='function')
def comments(request):
    return []


@pytest.fixture(scope='function')
def _driver(request, check_options, browser, report_folder,
            images, comments, screenshots, verbose, maximize_window,
            config_data, driver_paths, headless, pause):

    # Update settings from markers
    marker_window = markers.get_marker_window(request.node)
    config_data.update({'window': marker_window})

    marker_screenshots = markers.get_marker_screenshots(request.node)
    if marker_screenshots is not None:
        screenshots = marker_screenshots

    marker_browser = markers.get_marker_browser(request.node)
    if marker_browser is not None:
        browser = marker_browser

    marker_verbose = markers.get_marker_verbose(request.node)
    if marker_verbose is True:
        verbose = marker_verbose

    # Instantiate webdriver
    driver = None
    try:
        opt = browser_options(browser, config_data, headless)
        srv = browser_service(browser, config_data, driver_paths)
        if browser == "firefox":
            driver = WebDriverFirefox(options=opt, service=srv)
        elif browser == "chrome":
            driver = WebDriverChrome(options=opt, service=srv)
        elif browser == "chromium":
            driver = WebDriverChromium(options=opt, service=srv)
        elif browser == "edge":
            driver = WebDriverEdge(options=opt, service=srv)
        elif browser == "safari":
            driver = WebDriverSafari(options=opt, service=srv)
    except:
        if driver is not None:
            try:
                driver.quit()
            except:
                pass
        raise

    # Set driver attributes
    setattr(driver, "images", images)
    setattr(driver, "comments", comments)
    setattr(driver, "screenshots", screenshots)
    setattr(driver, "verbose", verbose)
    setattr(driver, "report_folder", report_folder)

    # Set capabilities
    set_driver_capabilities(driver, browser, config_data)

    # Set window
    if (maximize_window is True and 'maximize' not in marker_window) or \
            ('maximize' in marker_window and marker_window['maximize'] is True):
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
    wrapped_driver = EventFiringWebDriver(driver, event_listener)

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

    # Let's deal with exit status
    # update_test_status_counter(call, report)

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
        description = getattr(func, '__doc__')

        try:
            feature_request = item.funcargs['request']
        except:
            return
        # Is this plugin required/being used?
        try:
            feature_request.getfixturevalue('browser')
        except pytest.FixtureLookupError:
            return
        # Get test fixture values
        driver = feature_request.getfixturevalue('webdriver')
        images = feature_request.getfixturevalue('images')
        comments = feature_request.getfixturevalue('comments')
        screenshots = driver.screenshots
        verbose = driver.verbose
        description_tag = feature_request.getfixturevalue("description_tag")

        exception_logged = utils.append_header(call, report, extras, pytest_html, description, description_tag)

        if screenshots == "none":
            return

        if (description is not None or exception_logged is True) \
                and screenshots in ('all', 'manual'):
            extras.append(pytest_html.extras.html(f"<hr class=\"selenium_separator\">"))

        links = ""
        rows = ""
        if screenshots == 'all' and not verbose:
            for image in images:
                links += utils.get_anchor_tag(image, div=False)
        elif screenshots == 'manual' \
                or (screenshots == 'all' and verbose):
            # Check images and comments lists consistency
            if len(images) != len(comments):
                message = ("\"images\" and \"comments\" lists don't have the same length. "
                           "Screenshots won't be logged for this test.")
                utils.add_item_stderr_message(item, "ERROR: " + message)
                logger.append_report_error(item.location[0], item.location[2], message)
                report.extras = extras
                return
            for i in range(len(images)):
                rows += utils.get_table_row_tag(comments[i], images[i])
        elif screenshots == "last":
            image = utils.save_screenshot(driver, driver.report_folder)
            extras.append(pytest_html.extras.html(utils.get_anchor_tag(image)))
        if screenshots in ("failed", "manual"):
            xfail = hasattr(report, 'wasxfail')
            if xfail or report.outcome in ('failed', 'skipped'):
                image = utils.save_screenshot(driver, driver.report_folder)
                if screenshots == "manual":
                    # If this is the only screenshot, append it to the right of the table log row
                    if len(images) == 0:
                        extras.append(pytest_html.extras.html(utils.get_anchor_tag(image)))
                    # append the last screenshot in a new table log row
                    else:
                        if xfail or report.outcome == "failed":
                            event = "failure"
                        else:
                            event = "skip"
                        rows += utils.get_table_row_tag(
                                    f"Last screenshot before {event}",
                                    image,
                                    clazz="selenium_log_description"
                                )
                else:
                    extras.append(pytest_html.extras.html(utils.get_anchor_tag(image)))
        if links != "":
            extras.append(pytest_html.extras.html(links))
        if rows != "":
            rows = (
                "<table style=\"width: 100%;\">"
                "    <tbody>"
                + rows +
                "    </tbody>"
                "</table>"
            )
            extras.append(pytest_html.extras.html(rows))
        report.extras = extras
        # Check if there was a screenshot gathering failure
        if screenshots in ('all', 'manual'):
            for image in images:
                if image == f"screenshots{os.sep}error.png":
                    message = "Failed to gather screenshot(s)"
                    utils.add_item_stderr_message(item, "ERROR: " + message)
                    logger.append_report_error(item.location[0], item.location[2], message)
                    break


@pytest.hookimpl(trylast=True)
def pytest_configure(config):
    """ Register custom markers """
    config.addinivalue_line("markers", "browser(arg)")
    config.addinivalue_line("markers", "pause(arg)")
    config.addinivalue_line("markers", "window(kwargs)")
    config.addinivalue_line("markers", "screenshots(arg)")
    config.addinivalue_line("markers", "show_attributes")

    """ Add metadata. """
    metadata = config.pluginmanager.getplugin("metadata")
    if metadata:
        try:
            metadata = config._metadata
        except AttributeError:
            metadata = config.stash[metadata_key]
    try:
        browser = config.getoption("browser")
        pause = utils.getini(config, "pause")
        headless = config.getoption("headless")
        screenshots = config.getoption("screenshots")
        driver_config = utils.getini(config, "driver_config")
        metadata['Browser'] = browser.capitalize()
        metadata['Headless'] = str(headless).lower()
        metadata['Screenshots'] = screenshots
        metadata['Pause'] = pause + " second(s)"
        try:
            metadata['Selenium'] = version("selenium")
        except:
            metadata['Selenium'] = "unknown"
        if driver_config is not None and os.path.isfile(driver_config):
            if utils.load_json_yaml_file(driver_config) != {}:
                metadata["Driver configuration"] = \
                    (f"<a href='{driver_config}'>{driver_config}</a>"
                     f"<span style=\"color:green;\"> (valid)</span>")
            else:
                metadata["Driver configuration"] = \
                    (f"<a href='{driver_config}'>{driver_config}</a>"
                     f"<span style=\"color:red;\"> (invalid)</span>")
    except:
        pass
    finally:
        config._metadata = metadata


'''
passed  = 0
failed  = 0
xfailed = 0
skipped = 0
xpassed = 0
errors  = 0


def pytest_sessionfinish(session, exitstatus):
    """ Modify exit code. """
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


def update_test_status_counter(call, report):
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
        if (
            report.skipped and
            hasattr(call, 'excinfo') and
            call.excinfo is not None and
            call.excinfo.typename == 'Skipped'
        ):
            skipped += 1
        # For setup fixture
        if report.failed and call.excinfo is not None:
            errors += 1

    # For teardown fixture
    if call.when == 'teardown':
        if report.failed and call.excinfo is not None:
            errors += 1
 '''
