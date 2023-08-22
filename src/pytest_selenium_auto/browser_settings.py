import pytest
from selenium.webdriver.chrome.service   import Service as Service_Chrome
from selenium.webdriver.chromium.service import ChromiumService as Service_Chromium
from selenium.webdriver.firefox.service  import Service as Service_Firefox
from selenium.webdriver.edge.service     import Service as Service_Edge
from selenium.webdriver.safari.service   import Service as Service_Safari
from .configuration_loader import (
    get_options,
    get_service,
)


services = {
    'firefox':  Service_Firefox,
    'chrome':   Service_Chrome,
    'chromium': Service_Chromium,
    'edge':     Service_Edge,
    'safari':   Service_Safari,
}


@pytest.fixture(scope='session')
def browser_options(request, browser, config_data, headless):
    if browser is None:
        return None
    options = get_options(browser, config_data)

    for arg in get_arguments_from_markers(request.node):
        options.add_argument(arg)

    if headless is True:
        options.add_argument("--headless")

    if browser == "firefox":
        for name, value in get_preferences_from_markers(request.node).items():
            options.set_preference(name, value)

    return options


@pytest.fixture(scope='session')
def browser_service(request, browser, config_data, driver_paths):
    config_service = {}
    if 'browsers' in config_data and browser in config_data['browsers'] and 'service' in config_data['browsers'][browser]:
        config_service = config_data['browsers'][browser]['service']    
    if browser is None:
        return None
    # When driver configuration provided in pytest.ini file
    if driver_paths[browser] is not None and config_service == {}:
        return services[browser](executable_path=driver_paths[browser])
    # When driver configuration provided in JSON file
    elif config_service != {}:
        if driver_paths[browser] is not None:
            config_service['driver_path'] = driver_paths[browser]
        return get_service(browser, config_service)
    else:
        return services[browser]()


def get_arguments_from_markers(node):
    arguments = []
    for m in node.iter_markers("firefox_arguments"):
        arguments.extend(m.args)
    return arguments


def get_preferences_from_markers(node):
    preferences = dict()
    for mark in node.iter_markers("firefox_preferences"):
        preferences.update(mark.args[0])
    return preferences
