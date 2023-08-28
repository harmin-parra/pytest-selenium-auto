from selenium.webdriver.firefox.webdriver import WebDriver as WebDriverFirefox
from selenium.webdriver.chrome.webdriver import WebDriver as WebDriverChrome
from selenium.webdriver.chromium.webdriver import ChromiumDriver as WebDriverChromium
from selenium.webdriver.edge.webdriver import WebDriver as WebDriverEdge
from selenium.webdriver.safari.webdriver import WebDriver as WebDriverSafari
from selenium.webdriver.support.events import AbstractEventListener
import sys
import traceback
from . import utils


def try_catch_wrap(message):
    def decorator(func):
        def wrapped(*args, **kwargs):
            try:
                response = func(*args, **kwargs)
            except Exception as e:
                trace = traceback.format_exc()
                msg = f"{e}\n\n{trace}"
                print(msg, file=sys.stderr)
                response = utils.decorate_label(f"{message}<br/>{e}<br/>{trace}", "selenium_log_fatal")
            return response
        return wrapped
    return decorator


#
# Driver event listener
#
class CustomEventListener(AbstractEventListener):

    _element = None
    _value = None
    _url = None
    
    def after_navigate_to(self, url: str, driver) -> None:
        self._log_screenshot(driver)
        self._log_comment(
            driver,
            utils.decorate_label("Navigate to", "selenium_log_action") + \
            " " + \
            utils.decorate_label(url, "selenium_log_target")
        )
        self._url = driver.current_url

    def before_navigate_to(self, url: str, driver) -> None:
        pass

    def after_navigate_back(self, driver) -> None:
        self._log_screenshot(driver)
        self._log_comment(driver, utils.decorate_label("Navigate back", "selenium_log_action"))
        self._url = driver.current_url

    def before_navigate_back(self, driver) -> None:
        pass

    def after_navigate_forward(self, driver) -> None:
        self._log_screenshot(driver)
        self._log_comment(driver, utils.decorate_label("Navigate forward", "selenium_log_action"))
        self._url = driver.current_url

    def before_navigate_forward(self, driver) -> None:
        pass

    @try_catch_wrap("Undetermined event")
    def after_click(self, element, driver) -> None:
        self._log_screenshot(driver)
        if driver.current_url != self._url:
            self._url = driver.current_url
            self._log_comment(
                driver,
                utils.decorate_label("Click", "selenium_log_action") + \
                " element " + \
                utils.decorate_label(self._element, "selenium_log_target")
            )
        else:
            self._log_comment(
                driver,
                utils.decorate_label("Click", "selenium_log_action") + \
                " element " + \
                utils.decorate_label(self._get_web_element_attributes(element, driver), "selenium_log_target")
            )
        self._element = None

    def before_click(self, element, driver) -> None:
        self._element = self._get_web_element_attributes(element, driver)

    @try_catch_wrap("Undetermined event")
    def after_change_value_of(self, element, driver) -> None:
        self._log_screenshot(driver)
        self._element = self._get_web_element_attributes(element, driver)
        if self._value != element.get_attribute("value"):
            self._value = element.get_attribute("value")
            if len(self._value) > 0:
                self._log_comment(
                    driver,
                    utils.decorate_label("Send keys", "selenium_log_action") + \
                    " " + \
                    utils.decorate_quotation() + \
                    self._value + \
                    utils.decorate_quotation() + \
                    " to " + \
                    utils.decorate_label(self._get_web_element_attributes(element, driver), "selenium_log_target")
                )
            else:
                self._log_comment(
                    driver,
                    utils.decorate_label("Clear", "selenium_log_action") + \
                    " " + \
                    utils.decorate_label(self._get_web_element_attributes(element, driver), "selenium_log_target")
                )
        else:
            self._log_comment(
                driver,
                utils.decorate_label("Click", "selenium_log_action") + \
                " " + \
                utils.decorate_label(self._get_web_element_attributes(element, driver), "selenium_log_target")
            )
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

    def _log_comment(self, driver, comment):
        if driver.screenshots == 'all' and driver.verbose:
            driver.comments.append(comment)

    def _log_screenshot(self, driver):
        if driver.screenshots == 'all':
            driver.images.append(utils.save_screenshot(driver, driver.report_folder))

    @try_catch_wrap("Undetermined WebElement")
    def _get_web_element_attributes(self, element, driver):
        label = ""
        if driver.screenshots == 'all' and driver.verbose:
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
                label += f" name=\"{elem_name}\"";
            if elem_value is not None and type not in ("text", "textarea"):
                label += f" value=\"{elem_value}\"";
            if elem_classes is not None and len(elem_classes) > 0:
                label += f" class=\"{elem_classes}\"";
            if elem_text is not None and len(elem_text) > 0:
                label += f" text=\"{elem_text}\"";
            if elem_checked:
                label += " checked"
            label += "&gt;";
        return label


#
# WedDriver subclasses
#
class _Extras():

    images = None
    comments = None
    report_folder = None
    screenshots = None
    verbose = False

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
