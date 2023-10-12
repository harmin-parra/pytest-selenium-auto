from selenium.webdriver.firefox.webdriver import WebDriver as WebDriver_Firefox
from selenium.webdriver.chrome.webdriver import WebDriver as WebDriver_Chrome
from selenium.webdriver.chromium.webdriver import ChromiumDriver as WebDriver_Chromium
from selenium.webdriver.edge.webdriver import WebDriver as WebDriver_Edge
from selenium.webdriver.safari.webdriver import WebDriver as WebDriver_Safari
from selenium.webdriver.remote.webelement import By
from . import utils


#
# Utility superclasses
#
class _Extras:

    @staticmethod
    def log_screenshot(driver, comment=""):
        if comment is None:
            comment = ""
        if driver.screenshots in ('all', 'manual'):
            index = utils.counter()
            driver.images.append(utils.save_screenshot(driver, driver.report_folder, index))
            driver.comments.append({'comment': utils.escape_html(comment).replace('\n', '<br>')})
            if driver.log_page_source:
                driver.sources.append(utils.save_page_source(driver, driver.report_folder, index))
            else:
                driver.sources.append(None)

    @staticmethod
    def wrap_element(element, by, value):
        setattr(element, "_by", by)
        setattr(element, "_value", value)
        return element

    @staticmethod
    def wrap_elements(elements, by=By.ID, value=None):
        return [_Extras.wrap_element(element, by, value) for element in elements]


#
# WedDriver subclasses
#
class WebDriverFirefox(WebDriver_Firefox):

    def __init__(self, options=None, service=None):
        super().__init__(options=options, service=service)

    def log_screenshot(self, comment=""):
        _Extras.log_screenshot(self, comment)

    def find_element(self, by=By.ID, value=None):
        return _Extras.wrap_element(super().find_element(by, value), by, value)

    def find_elements(self, by=By.ID, value=None):
        return _Extras.wrap_elements(super().find_elements(by, value), by, value)


class WebDriverChrome(WebDriver_Chrome):

    def __init__(self, options=None, service=None):
        super().__init__(options=options, service=service)

    def log_screenshot(self, comment=""):
        _Extras.log_screenshot(self, comment)

    def find_element(self, by=By.ID, value=None):
        return _Extras.wrap_element(super().find_element(by, value), by, value)

    def find_elements(self, by=By.ID, value=None):
        return _Extras.wrap_elements(super().find_elements(by, value), by, value)


class WebDriverChromium(WebDriver_Chromium):

    def __init__(self, options=None, service=None):
        super().__init__(browser_name="Chromium", vendor_prefix="Chromium", options=options, service=service)

    def log_screenshot(self, comment=""):
        _Extras.log_screenshot(self, comment)

    def find_element(self, by=By.ID, value=None):
        return _Extras.wrap_element(super().find_element(by, value), by, value)

    def find_elements(self, by=By.ID, value=None):
        return _Extras.wrap_elements(super().find_elements(by, value), by, value)


class WebDriverEdge(WebDriver_Edge):

    def __init__(self, options=None, service=None):
        super().__init__(options=options, service=service)

    def log_screenshot(self, comment=""):
        _Extras.log_screenshot(self, comment)

    def find_element(self, by=By.ID, value=None):
        return _Extras.wrap_element(super().find_element(by, value), by, value)

    def find_elements(self, by=By.ID, value=None):
        return _Extras.wrap_elements(super().find_elements(by, value), by, value)


class WebDriverSafari(WebDriver_Safari):

    def __init__(self, options=None, service=None):
        super().__init__(options=options, service=service)

    def log_screenshot(self, comment=""):
        _Extras.log_screenshot(self, comment)

    def find_element(self, by=By.ID, value=None):
        return _Extras.wrap_element(super().find_element(by, value), by, value)

    def find_elements(self, by=By.ID, value=None):
        return _Extras.wrap_elements(super().find_elements(by, value), by, value)
