from selenium.webdriver.support.events import AbstractEventListener
from selenium.webdriver.remote.webelement import By
import re
import time
from . import utils


class CustomEventListener(AbstractEventListener):
    """ The WebDriver event listener. """

    def __init__(self, pause=0):
        self._description = None
        self._attributes = None
        self._locator = None
        self._action = None
        self._value = None
        self._url = None
        self.pause = pause

    def before_navigate_to(self, url: str, driver) -> None:
        pass

    def after_navigate_to(self, url: str, driver) -> None:
        _log_extras(
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
        _log_extras(
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
        _log_extras(
            driver,
            {
                'action': "Navigate forward",
            }
        )
        self._url = driver.current_url
        time.sleep(self.pause)

    def before_click(self, element, driver) -> None:
        self._action = _get_web_element_action(element, driver)
        self._attributes = _get_web_element_attributes(element, driver)
        self._locator = _get_web_element_locator(element, driver)
        self._description = getattr(element, "_description", None)

    @utils.try_catch_wrap_event("Undetermined event")
    def after_click(self, element, driver) -> None:
        if driver.current_url != self._url:
            self._url = driver.current_url
        else:
            self._action = _get_web_element_action(element, driver)
            self._attributes = _get_web_element_attributes(element, driver)
        action, value = _build_comment_from_metadata(driver, self._action, None, self._locator, self._description)
        _log_extras(
            driver,
            {
                'action': action,
                'value': value,
                'locator': self._locator,
                'attributes': self._attributes,
            }
        )
        self._action = None
        self._attributes = None
        self._locator = None
        self._description = None
        time.sleep(self.pause)

    def before_change_value_of(self, element, driver) -> None:
        self._value = element.get_attribute("value")

    @utils.try_catch_wrap_event("Undetermined event")
    def after_change_value_of(self, element, driver) -> None:
        self._attributes = _get_web_element_attributes(element, driver)
        self._locator = _get_web_element_locator(element, driver)
        description = getattr(element, "_description", None)
        if self._value != element.get_attribute("value"):
            self._value = element.get_attribute("value")
            if len(self._value) > 0:
                action, value = _build_comment_from_metadata(driver, "Send keys", self._value, None, description)
                _log_extras(
                    driver,
                    {
                        'action': action,
                        'value': value,
                        'locator': self._locator,
                        'attributes': self._attributes,
                    }
                )
            else:
                action, value = _build_comment_from_metadata(driver, "Clear", self._value, None, description)
                _log_extras(
                    driver,
                    {
                        'action': action,
                        'value': value,
                        'locator': self._locator,
                        'attributes': self._attributes,
                    }
                )
        else:
            action = _get_web_element_action(element, driver)
            _log_extras(
                driver,
                {
                    'action': action,
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


def _log_extras(driver, comment):
    """
    Logs the report HTML extras of the test step.
    
    Args:
        driver (WebDriver): The WebDriver.
        
        comment (dict): The comment to log.
            Examples:
                {
                    "action": str,
                    "url": str,
                    "value": str,
                    "locator": str,
                    "attributes": str
                }
                or
                {"comment": str}
    """
    if driver.screenshots == 'all' and driver.log_attributes:
        _log_comment(driver, comment)
    if driver.screenshots == 'all':
        index = utils.counter()
        _log_screenshot(driver, index)
        _log_page_source(driver, index)


def _log_comment(driver, comment):
    """
    Logs the comment of a test step.
    
    Args:
        driver (WebDriver): The WebDriver.
        
        comment (dict): The comment to log.
    """
    if driver.screenshots == 'all' and driver.log_attributes:
        driver.comments.append(comment)


def _log_screenshot(driver, index):
    """ Logs the browser screenshot of a test step. """
    driver.images.append(utils.save_screenshot(driver, driver.report_folder, index))


def _log_page_source(driver, index):
    """ Logs the HTML page source of a test step. """
    if driver.log_page_source:
        driver.sources.append(utils.save_page_source(driver, driver.report_folder, index))
    else:
        driver.sources.append(None)


@utils.try_catch_wrap_event("Undetermined WebElement")
def _get_web_element_action(element, driver):
    """
    Returns the action executed to some WebElements.
    
    Examples:
        'Click' for buttons.
        'Select' and 'Deselect' for select options.
        'Check' and 'Uncheck' for checkboxes and radio-buttons.
    """
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
def _get_web_element_attributes(element, driver):
    """ Returns a string representation of the WebElement HTML DOM attributes. """
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


def _get_web_element_locator(element, driver):
    """
    Returns a string representation of the locator from the
    WebElement metadata (_by and _value attributes).
    
    Returns:
        str: String representation of the WebElement locator.
    """
    if not (driver.screenshots == 'all' and driver.log_attributes):
        return None

    label = None
    index = element.get_attribute('index')
    by = getattr(element, "_by", None)
    value = getattr(element, "_value", None)

    # Select by value ?
    if by == By.CSS_SELECTOR:
        x = re.match(r'option\[value\s*=\s*"', value)
        if x is not None:
            element._by = "Select_By.VALUE"
            element._value = value[x.end(): -2]
    # Select by visible text ?
    if by == By.XPATH and value.startswith('.//option[normalize-space(.) = "'):
        element._by = "Select_By.VISIBLE_TEXT"
        element._value = value[32: -2]

    # Select by index ?
    if by == By.TAG_NAME and value == "option" and index is not None:
        element._by = "Select_By.INDEX"
        element._value = str(index)

    by = ""
    if hasattr(element, "_value") and hasattr(element, "_by"):
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
        elif isinstance(element._by, str):
            by = element._by
        if element._value.find(' ') != -1:
            label = f"{by} = \"{element._value}\""
        else:
            label = f"{by} = {element._value}"
    return label


def _build_comment_from_metadata(driver, action, value, locator, description):
    """
    Builds the description sentence of a test step based on the
    WebElement metadata, value attribute and
    the action executed on the WebElement.
    
    Args:
        action (str): The action executed on the WebElement.
            Examples: Click, Send keys, Clear, Navigate to, etc.
        
        value (str or None): The WebElement DOM 'value' attribute.
        
        locator (str, optional): The WebElement _locator string representation.
        
        description (str): The WebElement _description metadata.
    
    Returns:
        The action and value used to build the description of the test step.
    """
    if not (driver.screenshots == 'all' and driver.log_attributes):
        return None, None

    # Is this an input text without description ?
    if description is None:
        if action == "Clear":
            return action, None
        else:
            return action, value
    
    # Is this a select ?
    match = re.search(r"(\$select|\"\$select\"|'\$select')", description)
    if match is not None:
        description = description.replace(match.group(0), '').strip()
        value = locator[locator.index('=') + 2:]
    
    # Is this a checkbox, radio-button or textarea ?
    match = re.search(r"(\".*\"|'.*')", description)
    if match is not None:
        value = match.group(0).replace('"', '').replace("'", '')
        description = description.replace(match.group(0), '').strip()
    
    # Other objects
    if description.startswith("$action"):
        description = description.replace("$action", '')
        action += description
    else:
        action = description
    
    return action, value
