from selenium.webdriver.firefox.webdriver import WebDriver as WebDriverFirefox
from selenium.webdriver.chrome.webdriver import WebDriver as WebDriverChrome
from selenium.webdriver.chromium.webdriver import ChromiumDriver as WebDriverChromium
from selenium.webdriver.edge.webdriver import WebDriver as WebDriverEdge
from selenium.webdriver.safari.webdriver import WebDriver as WebDriverSafari
from selenium.webdriver.support.events import AbstractEventListener
from . import utils


#
# Driver event listener
#
class CustomEventListener(AbstractEventListener):

    def after_navigate_to(self, url: str, driver) -> None:
        self._log(driver)

    def after_navigate_back(self, driver) -> None:
        self._log(driver)

    def after_navigate_forward(self, driver) -> None:
        self._log(driver)

    def before_find(self, by, value, driver) -> None:
        pass

    def after_find(self, by, value, driver) -> None:
        pass

    def after_click(self, element, driver) -> None:
        self._log(driver)

    def after_change_value_of(self, element, driver) -> None:
        self._log(driver)

    def before_execute_script(self, script, driver) -> None:
        pass

    def after_execute_script(self, script, driver) -> None:
        pass

    def on_exception(self, exception, driver) -> None:
        pass

    def _log(self, driver):
        if driver.screenshots == 'all':
            driver.images.append(utils.save_screenshot(driver, driver.report_folder))


#
# WedDriver subclasses
#
class _Extras():

    images = None
    report_folder = None
    screenshots = None

    def log_screenshot(self):
        if self.screenshots == 'manual':
            self.images.append(utils.save_screenshot(self, self.report_folder))


class WebDriver_Firefox(WebDriverFirefox, _Extras):

    def __init__(self, options=None, service=None):
        super().__init__(options=options, service=service)


class WebDriver_Chrome(WebDriverChrome, _Extras):

    def __init__(self, options=None, service=None):
        super().__init__(options=options, service=service)


class WebDriver_Chromium(WebDriverChromium, _Extras):

    def __init__(self, options=None, service=None):
        super().__init__(browser_name="Chromium", vendor_prefix="Chromium", options=options, service=service)


class WebDriver_Edge(WebDriverEdge, _Extras):

    def __init__(self, options=None, service=None):
        super().__init__(options=options, service=service)


class WebDriver_Safari(WebDriverSafari, _Extras):

    def __init__(self, options=None, service=None):
        super().__init__(options=options, service=service)
