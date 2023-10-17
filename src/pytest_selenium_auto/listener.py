from selenium.webdriver.support.events import AbstractEventListener
from selenium.webdriver.remote.webelement import By
import re
import time
from . import (
    action_keywords,
    utils,
    value_keywords,
)


class CustomEventListener(AbstractEventListener):
    """ The WebDriver event listener. """

    def __init__(self, pause=0):
        self._attributes = None
        self._locator = None
        self._value = None
        self._url = None
        self.pause = pause

    def before_navigate_to(self, url: str, driver) -> None:
        pass

    def after_navigate_to(self, url: str, driver) -> None:
        _append_extras(
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
        _append_extras(
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
        _append_extras(
            driver,
            {
                'action': "Navigate forward",
            }
        )
        self._url = driver.current_url
        time.sleep(self.pause)

    def before_click(self, element, driver) -> None:
        self._attributes = _get_web_element_attributes(element, driver)
        self._locator = _get_web_element_locator(element, driver)

    @utils.try_catch_wrap_event("Undetermined event")
    def after_click(self, element, driver) -> None:
        if driver.current_url != self._url:
            self._url = driver.current_url
        else:
            self._attributes = _get_web_element_attributes(element, driver)
        action, value = _build_comment(driver, element, "Click", self._locator)
        _append_extras(
            driver,
            {
                'action': action,
                'value': value,
                'locator': self._locator,
                'attributes': self._attributes,
            }
        )
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
        if self._value != element.get_attribute("value"):
            self._value = element.get_attribute("value")
            if len(self._value) > 0:
                action, value = _build_comment(driver, element, "Send keys", self._locator)
                _append_extras(
                    driver,
                    {
                        'action': action,
                        'value': value,
                        'locator': self._locator,
                        'attributes': self._attributes,
                    }
                )
            else:
                action, value = _build_comment(driver, element, "Clear", self._locator)
                _append_extras(
                    driver,
                    {
                        'action': action,
                        'value': value,
                        'locator': self._locator,
                        'attributes': self._attributes,
                    }
                )
        else:
            action, value = _build_comment(driver, element, "Click", self._locator)
            _append_extras(
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
        self._value = None
        self._url = None

    def on_exception(self, exception, driver) -> None:
        pass


def _append_extras(driver, comment):
    """
    Logs the report HTML extras of the test step.

    Args:
        driver (WebDriver): The webdriver.

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
        _append_comment(driver, comment)
    if driver.screenshots == 'all':
        index = utils.counter()
        _append_screenshot(driver, index)
        _append_page_source(driver, index)


def _append_comment(driver, comment):
    """
    Logs the comment of a test step.

    Args:
        driver (WebDriver): The webdriver.

        comment (dict): The comment to log.
    """
    if driver.screenshots == 'all' and driver.log_attributes:
        driver.comments.append(comment)


def _append_screenshot(driver, index):
    """ Logs the browser screenshot of a test step. """
    driver.images.append(utils.save_screenshot(driver, driver.report_folder, index))


def _append_page_source(driver, index):
    """ Logs the HTML page source of a test step. """
    if driver.log_page_source:
        driver.sources.append(utils.save_page_source(driver, driver.report_folder, index))
    else:
        driver.sources.append(None)


@utils.try_catch_wrap_event("Undetermined WebElement")
def _get_web_element_attributes(element, driver):
    """ Returns a string representation of the webelement HTML attributes. """
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
    webelement metadata (_by and _value attributes).

    Returns:
        str: String representation of the webelement locator.
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


def _build_comment(driver, element, action, locator):
    """
    Builds the comment of a test step based on the
    webdriver metadata, value attribute and
    the action executed on the webdriver.

    A comment has one of the following forms:
        - {action} "{value}"
        - {action}

    Args:
        driver (WebDriver): The webdriver.

        element (WebElement): The webelement.

        action (str): The default action for the webelement.
            Examples: Click, Send keys, Clear, Navigate to, etc.

        locator (str, optional): The webelement locator string representation.

    Returns:
        (str, str): The action and the value to build the comment of a test step.
    """
    if not (driver.screenshots == 'all' and driver.log_attributes):
        return None, None

    description = getattr(element, "_description", None)

    value, description = _get_comment_value(element, description)

    # Is this an input text without description ?
    if description is None:
        if action == "Clear":
            return action, None
        else:
            return action, value

    # Is this a select ?
    # Replace $by by the locator and use it as value for the comment.
    match = re.search(r"(\$by|\"\$by\"|'\$by')", description)
    if match is not None:
        description = description.replace(match.group(0), '').strip()
        value = locator[locator.index('=') + 2:]

    action = _get_comment_action(element, description)

    return action, value


def _get_comment_action(element, description):
    """ Returns the action for the comment of a test step. """
    try:
        is_selected = element.is_selected()
    except:
        is_selected = None
    if description is None or is_selected is None:
        return description

    for word in action_keywords.keys():
        if description.startswith(word):
            action = action_keywords[word][0] if is_selected else action_keywords[word][1]
            description = description.replace(word, action)
            break

    return description


def _get_comment_value(element, description):
    """
    Returns the value for the comment of a test step.
    Removes the value from the description.

    Returns:
        (str, str): The value and the remaining of the description.
    """
    value = None

    # Is this an input text ?
    try:
        value = element.get_attribute("value")
    except:
        pass

    if description is not None:
        # Is a value keyword present in description ?
        # Then, extract the corresponding webelement attribute.
        for word in value_keywords:
            if word in description:
                try:
                    value = element.get_attribute(word[1:])
                    description = description.replace(word, value).strip()
                except:
                    pass
                finally:
                    break

        # Is there is a string surrounded by quotation?
        # Use it as value for the comment.
        exp = re.search(r"(\".*\"|'.*')", description)
        if exp is not None:
            value = exp.group(0).replace('"', '').replace("'", '')
            description = description.replace(exp.group(0), '').strip()

    return value, description
