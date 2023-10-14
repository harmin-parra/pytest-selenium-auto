from selenium.webdriver.support.events import EventFiringWebDriver
from selenium.webdriver.remote.webelement import By
from . import utils


class CustomEventFiringWebDriver(EventFiringWebDriver):


    def wrap_element(self, element, by, value, description=None):
        setattr(element, "_by", by)
        setattr(element, "_value", value)
        if description is not None:
            setattr(element, "_description", description)

    def find_element(self, by=By.ID, value=None, description=None):
        elem = super().find_element(by, value)
        self.wrap_element(elem._webelement, by, value, description)
        return elem

    def find_elements(self, by=By.ID, value=None, description=None):
        elems = super().find_elements(by, value)
        for elem in elems:
            self.wrap_element(elem._webelement, by, value, description)
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
