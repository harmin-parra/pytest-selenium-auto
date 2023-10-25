from selenium.webdriver.chrome.service import Service as Service_Chrome
from selenium.webdriver.chromium.service import ChromiumService as Service_Chromium
from selenium.webdriver.firefox.service import Service as Service_Firefox
from selenium.webdriver.edge.service import Service as Service_Edge
from selenium.webdriver.safari.service import Service as Service_Safari
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


def browser_options(browser, config, headless):
    """
    Loads browser options from plugin options and JSON/YAML webdriver configuration.
    
    Args:
        browser (str): The 'browser' command-line option value.
        
        config (dict): The webdriver configuration loaded from JSON/YAML file.

        headless (bool): The 'headless' INI option value.
        
    Returns:
        selenium.webdriver.<browser>.options.Options: The options instance.
    """
    if browser is None:
        return None

    options = get_options(browser, config)
    # window = markers.get_marker_window(request.node)
    if (
        headless is True or
        (
            'window' in config and
            'headless' in config['window'] and
            config['window']['headless'] is True
        )
    ):
        options.add_argument("--headless")
    # options.update(markers.get_marker_options(request.node))
    return options


def browser_service(browser, config, driver_paths):
    """
    Loads browser service from plugin options and JSON/YAML webdriver configuration.
    
    Args:
        browser (str): The 'browser' command-line option value.
        
        config (dict): The webdriver configuration loaded from JSON/YAML file.

        driver_paths (dict[str,str]): The webdriver filepath INI option values.
        
    Returns:
        selenium.webdriver.<browser>.service.Service: The service instance.
    """
    config_service = {}
    if (
        'browsers' in config and
        browser in config['browsers'] and
        'service' in config['browsers'][browser]
    ):
        config_service = config['browsers'][browser]['service']
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
