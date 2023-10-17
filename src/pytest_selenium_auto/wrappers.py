from selenium.webdriver.support.event_firing_webdriver import EventFiringWebElement, EventFiringWebDriver
from selenium.webdriver.remote.webelement import By
from selenium.webdriver.support.select import Select
from . import utils


def wrap_driver(driver, images, sources, comments, screenshots, report_folder, log_attributes, log_page_source):
    """
    Adds metadata to a WebDriver.
    
    Args:
        images (list[str]): The list of screenshots filenames.
        
        sources (list[str]): The list of web page sources filenames.
        
        comments (list[str]): The list of test steps comments.
        
        report_folder (str): The HTML report folder.
        
        log_attributes (bool): Whether to log WebElement DOM attributes.
        
        log_page_source (bool): Whether to log web page sources.
    """
    setattr(driver, "images", images)
    setattr(driver, "sources", sources)
    setattr(driver, "comments", comments)
    setattr(driver, "screenshots", screenshots)
    setattr(driver, "report_folder", report_folder)
    setattr(driver, "log_attributes", log_attributes)
    setattr(driver, "log_page_source", log_page_source)


def wrap_element(element, by, value, description=None):
    """
    Adds metadata to a WebElement.
    
    Args:
        element (WebElement): The WebElement to modify.
        
        by (By): The locator strategy.
        
        value (str): The locator value.
        
        description (str): The description pattern of the webelement interaction.
    """
    setattr(element, "locator_by", by)
    setattr(element, "locator_value", value)
    setattr(element, "description", description)


class CustomEventFiringWebDriver(EventFiringWebDriver):
    """
    EventFiringWebDriver wrapper.
    
    Overrides find_element and find_elements methods.
    Adds log_screenshot method.
    """

    def find_element(self, by=By.ID, value=None, description=None):
        elem = super().find_element(by, value)
        wrap_element(elem.wrapped_element, by, value, description)
        return elem

    def find_elements(self, by=By.ID, value=None, description=None):
        elems = super().find_elements(by, value)
        for elem in elems:
            wrap_element(elem.wrapped_element, by, value, description)
        return elems

    def log_screenshot(self, comment=""):
        driver = self.wrapped_driver
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


class CustomEventFiringWebElement(EventFiringWebElement):
    """
    EventFiringWebElement wrapper.
    Overrides find_element and find_elements methods.
    """

    def find_element(self, by=By.ID, value=None):
        elem = super().find_element(by, value)
        description = getattr(self.wrapped_element.wrapped_element, "description", None)
        wrap_element(elem.wrapped_element, by, value, description)
        return elem

    def find_elements(self, by=By.ID, value=None):
        elems = super().find_elements(by, value)
        description = getattr(self.wrapped_element.wrapped_element, "description", None)
        for elem in elems:
            wrap_element(elem.wrapped_element, by, value, description)
        return elems


class CustomSelect(Select):
    """ Select wrapper. """
    
    def __init__(self, webelement, driver) -> None:
        elem = CustomEventFiringWebElement(webelement, driver)
        super().__init__(elem)
