from selenium.webdriver.firefox.webdriver import WebDriver as WebDriver_Firefox
from selenium.webdriver.chrome.webdriver import WebDriver as WebDriver_Chrome
from selenium.webdriver.chromium.webdriver import ChromiumDriver as WebDriver_Chromium
from selenium.webdriver.edge.webdriver import WebDriver as WebDriver_Edge
from selenium.webdriver.safari.webdriver import WebDriver as WebDriver_Safari
from selenium.webdriver.support.events import AbstractEventListener
from selenium.webdriver.remote.webelement import By
import time
from . import utils


#
# Driver event listener
#
class CustomEventListener(AbstractEventListener):

    def __init__(self, pause=0):
        self._attributes = None
        self._locator = None
        self._action = None
        self._value = None
        self._url = None
        self.pause = pause

    def before_navigate_to(self, url: str, driver) -> None:
        pass

    def after_navigate_to(self, url: str, driver) -> None:
        self._log_resources(driver)
        self._log_comment(
            driver,
            {
                'action': "Navigate to",
                'url': url,
            }
        )
        self._url = driver.current_url
        time.sleep(self.pause)

    def before_navigate_back(self, driver) -> None:
        pass

    def after_navigate_back(self, driver) -> None:
        self._log_resources(driver)
        self._log_comment(
            driver,
            {
                'action': "Navigate back",
            }
        )
        self._url = driver.current_url
        time.sleep(self.pause)

    def before_navigate_forward(self, driver) -> None:
        pass

    def after_navigate_forward(self, driver) -> None:
        self._log_resources(driver)
        self._log_comment(
            driver,
            {
                'action': "Navigate forward",
            }
        )
        self._url = driver.current_url
        time.sleep(self.pause)

    def before_click(self, element, driver) -> None:
        self._action = self._get_web_element_action(element, driver)
        self._attributes = self._get_web_element_attributes(element, driver)
        self._locator = self._get_web_element_locator(element, driver)

    @utils.try_catch_wrap_event("Undetermined event")
    def after_click(self, element, driver) -> None:
        self._log_resources(driver)
        if driver.current_url != self._url:
            self._url = driver.current_url
        else:
            self._attributes = self._get_web_element_attributes(element, driver)
            self._locator = self._get_web_element_locator(element, driver)
            self._action = self._get_web_element_action(element, driver)
        self._log_comment(
            driver,
            {
                'action': self._action,
                'locator': self._locator,
                'attributes': self._attributes,
            }
        )
        self._action = None
        self._attributes = None
        self._locator = None
        time.sleep(self.pause)

    def before_change_value_of(self, element, driver) -> None:
        self._value = element.get_attribute("value")

    @utils.try_catch_wrap_event("Undetermined event")
    def after_change_value_of(self, element, driver) -> None:
        self._log_resources(driver)
        self._attributes = self._get_web_element_attributes(element, driver)
        self._locator = self._get_web_element_locator(element, driver)
        if self._value != element.get_attribute("value"):
            self._value = element.get_attribute("value")
            if len(self._value) > 0:
                self._log_comment(
                    driver,
                    {
                        'action': "Send keys",
                        'value': self._value,
                        'locator': self._locator,
                        'attributes': self._attributes,
                    }
                )
            else:
                self._log_comment(
                    driver,
                    {
                        'action': "Clear",
                        'locator': self._locator,
                        'attributes': self._attributes,
                    }
                )
        else:
            self._log_comment(
                driver,
                {
                    'action': self._get_web_element_action(element, driver),
                    'locator': self._locator,
                    'attributes': self._attributes,
                }
            )
        self._value = None
        time.sleep(self.pause)

    def before_quit(self, driver) -> None:
        self._attributes = None
        self._locator = None
        self._action = None
        self._value = None
        self._url = None

    def on_exception(self, exception, driver) -> None:
        pass

    def _log_comment(self, driver, comment):
        """
        comment: dict{"action": str, "url": str, "value": str, "locator": str, "attributes": str}
                 or
                 dict{"comment": str}
        """
        if driver.screenshots == 'all' and driver.log_attributes:
            driver.comments.append(comment)

    def _log_resources(self, driver):
        if driver.screenshots == 'all':
            index = utils.counter()
            self._log_screenshot(driver, index)
            self._log_page_source(driver, index)

    def _log_screenshot(self, driver, index):
        driver.images.append(utils.save_screenshot(driver, driver.report_folder, index))

    def _log_page_source(self, driver, index):
        if driver.log_page_source:
            driver.sources.append(utils.save_page_source(driver, driver.report_folder, index))
        else:
            driver.sources.append(None)

    @utils.try_catch_wrap_event("Undetermined WebElement")
    def _get_web_element_action(self, element, driver):
        if not (driver.screenshots == 'all' and driver.log_attributes):
            return None

        elem_tag = element.tag_name
        elem_type = element.get_dom_attribute("type")
        elem_checked = element.is_selected()

        if elem_tag == 'option':
            if elem_checked:
                return "Select"
            else:
                return "Deselect"
        if elem_tag == 'input' and elem_type in ('radio', 'checkbox'):
            if elem_checked:
                return "Check"
            else:
                return "Uncheck"
        else:
            return "Click"

    @utils.try_catch_wrap_event("Undetermined WebElement")
    def _get_web_element_attributes(self, element, driver):
        if not (driver.screenshots == 'all' and driver.log_attributes):
            return None

        elem_tag = element.tag_name
        elem_id = element.get_dom_attribute("id")
        elem_name = element.get_dom_attribute("name")
        elem_type = element.get_dom_attribute("type")
        elem_value = element.get_attribute("value")
        elem_checked = element.is_selected()
        elem_classes = element.get_dom_attribute("class")
        elem_href = element.get_dom_attribute("href")
        elem_text = element.text

        label = "&lt;"
        if elem_tag is not None:
            label += elem_tag
        if elem_href is not None and len(elem_href) > 0:
            label += f" href=\"{elem_href}\""
        if elem_type is not None and len(elem_type) > 0:
            label += f" type=\"{elem_type}\""
        if elem_id is not None and len(elem_id) > 0:
            label += f" id=\"{elem_id}\""
        if elem_name is not None and len(elem_name) > 0:
            label += f" name=\"{elem_name}\""
        if elem_value is not None and type not in ("text", "textarea"):
            label += f" value=\"{elem_value}\""
        if elem_classes is not None and len(elem_classes) > 0:
            label += f" class=\"{elem_classes}\""
        if elem_text is not None and len(elem_text) > 0:
            label += f" text=\"{elem_text}\""
        if elem_checked:
            label += " checked"
        label += "&gt;"
        return label

    def _get_web_element_locator(self, element, driver):
        if not (driver.screenshots == 'all' and driver.log_attributes):
            return None

        label = None
        if hasattr(element, "_value") and hasattr(element, "_by"):
            by = ""
            if element._by == By.ID:
                by = "By.ID"
            elif element._by == By.NAME:
                by = "By.NAME"
            elif element._by == By.CLASS_NAME:
                by = "By.CLASS_NAME"
            elif element._by == By.CSS_SELECTOR:
                by = "By.CSS_SELECTOR"
            elif element._by == By.LINK_TEXT:
                by = "By.LINK_TEXT"
            elif element._by == By.PARTIAL_LINK_TEXT:
                by = "By.PARTIAL_LINK_TEXT"
            elif element._by == By.TAG_NAME:
                by = "By.TAG_NAME"
            elif element._by == By.XPATH:
                by = "By.XPATH"
            if element._value.find(' ') != -1:
                label = f"{by} = \"{element._value}\""
            else:
                label = f"{by} = {element._value}"
        return label


#
# WedDriver subclasses
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
