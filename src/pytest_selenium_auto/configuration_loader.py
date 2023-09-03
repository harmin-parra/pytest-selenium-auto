from selenium.webdriver.common import proxy
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.options import Options as Options_Firefox
from selenium.webdriver.firefox.service import Service as Service_Firefox
from selenium.webdriver.chrome.options import Options as Options_Chrome
from selenium.webdriver.chrome.service import Service as Service_Chrome
from selenium.webdriver.chromium.options import ChromiumOptions as Options_Chromium
from selenium.webdriver.chromium.service import ChromiumService as Service_Chromium
from selenium.webdriver.edge.options import Options as Options_Edge
from selenium.webdriver.edge.service import Service as Service_Edge
from selenium.webdriver.safari.options import Options as Options_Safari
from selenium.webdriver.safari.service import Service as Service_Safari
import traceback
from . import logger


def get_options(browser, config):
    options = None
    try:
        if browser == "firefox":
            options = Options_Firefox()
            if 'browsers' in config and browser in config['browsers'] and 'profile' in config['browsers'][browser]:
                _set_profile(options, config['browsers'][browser]['profile'])
        if browser == "chrome":
            options = Options_Chrome()
        if browser == "chromium":
            options = Options_Chromium()
        if browser == "edge":
            options = Options_Edge()
        if browser == "safari":
            options = Options_Safari()
    except:
        raise

    if 'capabilities' in config:
        _set_general_options(options, config['capabilities'])
    if 'window' in config and 'headless' in config['window']:
        _set_headless(options, config['window']['headless'])
    if 'browsers' in config and browser in config['browsers'] and 'options' in config['browsers'][browser]:
        _set_specific_options(options, config['browsers'][browser]['options'])

    return options


def get_service(browser, config):
    try:
        if browser == "firefox":
            service = Service_Firefox(
                executable_path=config.get('driver_path'),
                port=config.get('port', 0),
                service_args=config.get('args', None),
                log_output=config.get('log_output', None),
            )
        if browser == "chrome":
            service = Service_Chrome(
                executable_path=config.get('driver_path'),
                port=config.get('port', 0),
                service_args=config.get('args', None),
                log_output=config.get('log_output', None),
            )
        if browser == "chromium":
            service = Service_Chromium(
                executable_path=config.get('driver_path'),
                port=config.get('port', 0),
                service_args=config.get('args', None),
                log_output=config.get('log_output', None),
            )
        if browser == "edge":
            service = Service_Edge(
                executable_path=config.get('driver_path'),
                port=config.get('port', 0),
                service_args=config.get('args', None),
                log_output=config.get('log_output', None),
            )
        if browser == "safari":
            service = Service_Safari(
                executable_path=config.get('driver_path'),
                port=config.get('port', 0),
                service_args=config.get('args', None),
                log_output=config.get('log_output', None),
            )
    except:
        raise
    return service


def set_driver_capabilities(driver, browser, config):
    if 'capabilities' in config:
        if 'timeouts' in config['capabilities']:
            _set_timeouts(driver, config['capabilities']['timeouts'])
        if 'window' in config:
            _set_window(driver, config['window'])
        if 'window' in config and 'maximize' in config['window'] and config['window']['maximize'] is True:
            driver.maximize_window()
        if browser == 'firefox' and 'browsers' in config and 'firefox' in config['browsers'] and 'addons' in config['browsers']['firefox']:
            _install_addons(driver, config['browsers'][browser]['addons'])


def _set_proxy(options, config):
    if 'proxyType' in config and isinstance(config['proxyType'], str):
        if config['proxyType'].lower() == "manual":
            config['proxyType'] = proxy.ProxyType.MANUAL
        elif config['proxyType'].lower() == "pac":
            config['proxyType'] = proxy.ProxyType.PAC
        elif config['proxyType'].lower() == "direct":
            config['proxyType'] = proxy.ProxyType.DIRECT
        elif config['proxyType'].lower() == "autodetect":
            config['proxyType'] = proxy.ProxyType.AUTODETECT
        elif config['proxyType'].lower() == "system":
            config['proxyType'] = proxy.ProxyType.SYSTEM
        else:
            config['proxyType'] = proxy.ProxyType.UNSPECIFIED
    # Remove ftpProxy key
    config.pop('ftpProxy', None)
    options.proxy = proxy.Proxy(config)


def _set_insecure_certificates(options, value):
    options.set_capability("acceptInsecureCerts", value)


def _set_page_load_strategy(options, value):
    options.set_capability("pageLoadStrategy", value)


def _set_headless(options, value):
    if value is True:
        options.add_argument("--headless")


def _set_timeouts(driver, config):
    if 'implicit' in config and hasattr(driver, 'implicit_wait'):
        driver.implicit_wait(config['implicit'])
    if 'script' in config:
        driver.set_script_timeout(config['script'])
    if 'pageLoad' in config:
        driver.set_page_load_timeout(config['pageLoad'])


def _set_window(driver, config):
    if 'maximize' in config and config['maximize'] is True:
        driver.maximize_window()
    if 'size' in config:
        driver.set_window_size(config['size']['width'], config['size']['height'])
    if 'position' in config:
        driver.set_window_position(config['position']['x'], config['position']['y'])
    if 'rect' in config:
        driver.set_window_rect(config['rect']['x'], config['rect']['y'], config['rect']['width'], config['rect']['height'])


def _set_profile(options, config):
    try:
        profile = FirefoxProfile(config.get('directory', None))
        if 'preferences' in config:
            for key in config['preferences']:
                profile.set_preference(key, config['preferences'][key])
        if 'extensions' in config:
            for ext in config['extensions']:
                profile.add_extension(ext)
        options.profile = profile
    except Exception as e:
        trace = traceback.format_exc()
        logger.append_driver_error("Error creating browser's profile.", str(e), trace)
        raise e


def _install_addons(driver, addons):
    for addon in addons:
        try:
            driver.install_addon(addon)
        except:
            raise


def _set_general_options(options, config):
    if 'proxy' in config:
        _set_proxy(options, config['proxy'])
    if 'acceptInsecureCerts' in config:
        _set_insecure_certificates(options, config['acceptInsecureCerts'])
    if 'pageLoadStrategy' in config:
        _set_page_load_strategy(options, config['pageLoadStrategy'])


def _set_specific_options(options, config):
    for opt in config:
        if opt == "arguments":
            for arg in config['arguments']:
                try:
                    options.add_argument(arg)
                except:
                    raise
        elif opt == "preferences":
            for pref in config['preferences']:
                try:
                    options.set_preference(pref, config['preferences'][pref])
                except:
                    raise
        elif opt == "extensions":
            for ext in config['extensions']:
                try:
                    options.add_extension(ext)
                except:
                    raise
        elif hasattr(options, opt):
            try:
                setattr(options, opt, config[opt])
            except:
                raise
