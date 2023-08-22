from selenium.webdriver.support.events import AbstractEventListener
from . import utils


#
# Driver event listener
#
class CustomEventListener(AbstractEventListener):

    def after_navigate_to(self, url: str, driver) -> None:
        if driver.screenshots == 'all':
            utils.save_screenshot(driver, driver.images, driver.folder_report)

    def after_navigate_back(self, driver) -> None:
        if driver.screenshots == 'all':
            utils.save_screenshot(driver, driver.images, driver.folder_report)

    def after_navigate_forward(self, driver) -> None:
        if driver.screenshots == 'all':
            utils.save_screenshot(driver, driver.images, driver.folder_report)

    def before_find(self, by, value, driver) -> None:
        pass

    def after_find(self, by, value, driver) -> None:
        pass

    def after_click(self, element, driver) -> None:
        if driver.screenshots == 'all':
            utils.save_screenshot(driver, driver.images, driver.folder_report)

    def after_change_value_of(self, element, driver) -> None:
        if driver.screenshots == 'all':
            utils.save_screenshot(driver, driver.images, driver.folder_report)

    def before_execute_script(self, script, driver) -> None:
        pass

    def after_execute_script(self, script, driver) -> None:
        pass

    def on_exception(self, exception, driver) -> None:
        pass
