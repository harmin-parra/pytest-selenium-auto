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

    _element = None
    _value = None
    _url = None
    
    def after_navigate_to(self, url: str, driver) -> None:
        self._log(driver, utils.decorate_label("Navigate to", "action") + " " + utils.decorate_label(url, "target"))
        self._url = driver.current_url

    def before_navigate_to(self, url: str, driver) -> None:
        pass

    def after_navigate_back(self, driver) -> None:
        self._log(driver, utils.decorate_label("Navigate back", "action"))
        self._url = driver.current_url

    def before_navigate_back(self, driver) -> None:
        pass

    def after_navigate_forward(self, driver) -> None:
        self._log(driver, utils.decorate_label("Navigate forward", "action"))
        self._url = driver.current_url

    def before_navigate_forward(self, driver) -> None:
        pass

    def after_click(self, element, driver) -> None:
        if driver.current_url != self._url:
            self._url = driver.current_url
            self._log(driver, utils.decorate_label("Click", "action") + " element " + utils.decorate_label(self._element, "target"))
        else:
            self._log(driver, "Click element " + self._get_web_element_attributes(element))
        self._element = None

    def before_click(self, element, driver) -> None:
        self._element = self._get_web_element_attributes(element)

    def after_change_value_of(self, element, driver) -> None:
        self._element = self._get_web_element_attributes(element)
        if self._value != element.get_attribute("value"):
            self._value = element.get_attribute("value")
            if len(self._value) > 0:
                self._log(driver, utils.decorate_label("Send keys", "action") + " " + utils.decorate_quotation() + self._value + utils.decorate_quotation() + " to " + utils.decorate_label(self._get_web_element_attributes(element), "target"))
            else:
                self._log(driver, utils.decorate_label("Clear", "action") + " " + utils.decorate_label(self._get_web_element_attributes(element), "target"))
        else:
            self._log(driver, utils.decorate_label("Click", "action") + " " + utils.decorate_label(self._get_web_element_attributes(element), "target"))
        self._value = None

    def before_change_value_of(self, element, driver) -> None:
        self._value = element.get_attribute("value")

    def after_execute_script(self, script, driver) -> None:
        pass

    def before_execute_script(self, script, driver) -> None:
        pass

    def before_quit(self, driver) -> None:
        self._element = None
        self._value = None
        self._url = None

    def on_exception(self, exception, driver) -> None:
        pass

    def _log(self, driver, comment):
        if driver.screenshots == 'all':
            driver.images.append(utils.save_screenshot(driver, driver.report_folder))
            driver.comments.append(comment)

    def _get_web_element_attributes(self, element):
        elem_tag = element.tag_name
        elem_id = element.get_dom_attribute("id")
        elem_name = element.get_dom_attribute("name")
        elem_type = element.get_dom_attribute("type")
        elem_value = element.get_attribute("value")
        elem_checked = element.is_selected()
        elem_classes = element.get_dom_attribute("class")
        elem_href = element.get_dom_attribute("href")
        elem_text = element.text

        result = "&lt;"
        if elem_tag is not None:
            result += elem_tag
        if elem_href is not None and len(elem_href) > 0:
            result += f" href=\"{elem_href}\""
        if elem_type is not None and len(elem_type) > 0:
            result += f" type=\"{elem_type}\""
        if elem_id is not None and len(elem_id) > 0:
            result += f" id=\"{elem_id}\""
        if elem_name is not None and len(elem_name) > 0:
            result += f" name=\"{elem_name}\"";
        if elem_value is not None and type not in ("text", "textarea"):
            result += f" value=\"{elem_value}\"";
        if elem_classes is not None and len(elem_classes) > 0:
            result += f" class=\"{elem_classes}\"";
        if elem_text is not None and len(elem_text) > 0:
            result += f" text=\"{elem_text}\"";
        if elem_checked:
            result += " checked"
        result += "&gt;";
        return utils.decorate_label(result, "target");


#
# WedDriver subclasses
#
class _Extras():

    images = None
    comments = None
    report_folder = None
    screenshots = None

    def log_screenshot(self, comment=""):
        if self.screenshots == 'manual':
            self.images.append(utils.save_screenshot(self, self.report_folder))
            self.comments.append(comment)


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
