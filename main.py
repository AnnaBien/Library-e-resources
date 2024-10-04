import time
import datetime

from os import path
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from logger import create_logger


class RequestNotSend(Exception):
    def __init__(self):
        self.logger = create_logger(name=self.__class__.__name__, level='error')
        self.logger.exception('Task has failed')


class PageNotAvailable(Exception):
    def __init__(self, site_address):
        self.logger = create_logger(name=self.__class__.__name__, level='error')
        self.logger.exception(f'The website is not available: {site_address}')


class RequestResourceAccess:

    """
    A class that provides functionality for requesting access to library e-resources.
    The Selenium library is used to handle the form on the Rajska library website.
    The form needs to be sent every first day of the month.
    """

    def __init__(self):
        self.driver = webdriver.Remote(command_executor='http://127.0.0.1:4444', options=Options())
        self._library_card = '<your_library_card_number>'
        self._email_address = '<your_email_address>'
        self._e_resource_name = 'legimi'  # legimi or empik
        self.logger = create_logger(self.__class__.__name__, level='debug')

    def _find_element_by_xpath(self, xpath: str):
        """
        Try to find an element by given xpath. If element cannot be found raise RequestNotSend exception.
        :param xpath: xpath to the element
        :return:
        """

        try:
            return self.driver.find_element(by=By.XPATH, value=xpath)
        except NoSuchElementException as elem_not_found:
            self.logger.error(f'The element cannot be found by given xpath: {xpath}')
            self.driver.quit()
            raise RequestNotSend from elem_not_found

    def _save_screenshot(self):
        """
        Save a screenshot in the current directory.
        :return:
        """

        timestamp = datetime.datetime.now().strftime('%H-%M-%S_%d-%m-%Y')
        screenshot_filepath = path.join(path.dirname(__file__), f'screenshot_{timestamp}.png')
        screenshot_saved = self.driver.save_screenshot(filename=screenshot_filepath)
        if screenshot_saved:
            self.logger.debug(f'Screenshot saved at {screenshot_filepath}')
        else:
            self.logger.warning(f'Error while saving a screenshot')

    def _go_to_site_if_available(self, site_address):
        """
        Check if site contains an error (POST response is still 200).
        Terminate if website cannot be reached.
        :return:
        """

        self.driver.get(site_address)
        try:
            self.driver.find_element(by=By.CLASS_NAME, value='error')
        except NoSuchElementException:
            self.logger.info(f'Moved to site: {site_address}')
            return
        self.driver.quit()
        raise RequestNotSend from PageNotAvailable(site_address)

    def _wait_until_form_is_available(self, counter: int = 24, duration: int = 5):
        """
        Wait until the form becomes available on the website.

        :param counter: Number of repetitions of the check
        :param duration: Time duration between repetitions [s]
        :return:
        """

        while counter > 0:
            try:
                self.driver.refresh()
                self.driver.find_element(by=By.LINK_TEXT, value='E-Zasoby')  # TODO: Check whether it is valid
                break
            except NoSuchElementException:
                self.logger.warning(f'The form is still unavailable, waiting {duration}s to retry...')
                counter -= 1
                time.sleep(duration)
        else:
            self.logger.error('The link to the form cannot be found.')
            self.driver.quit()
            raise RequestNotSend
        self.logger.info('The form is available!')

    def _go_to_form(self):
        """
        Go to Rajska library website and find the form to request e-resources access.
        If the link to the form cannot be found raise RequestNotSend exception.
        Note: Form opens in a new tab

        :return: None
        """

        self._go_to_site_if_available('https://www.rajska.info/pobierz-kody-kolejne-platformy-czekaja')
        try:
            href_elem = self.driver.find_element(by=By.LINK_TEXT, value='formularz zgłoszeniowy')
            href_elem.click()
        except NoSuchElementException as link_not_found:
            self.logger.error('The link to the form cannot be found.')
            self.driver.quit()
            raise RequestNotSend from link_not_found

        current_window = self.driver.current_window_handle
        for window in self.driver.window_handles:
            if window != current_window:
                self.driver.switch_to.window(window)
                self.logger.info(f"Switched to the form's window")
                break

    def _fill_form(self):
        """
        Fill form with:
            - your library card number
            - your e-mail address to which an access code will be sent
            - the e-resource type: legimi or empik

        Save a screenshot of the filled form.
        :return: None
        """

        card_no_input = self._find_element_by_xpath(
            xpath='//div[contains(.//span, "Numer karty czytelnika WBP w Krakowie:")]//input[@type="text"]'
        )
        self.logger.debug('Found the input element for the library card number')
        card_no_input.send_keys(self._library_card)
        self.logger.info('Successfully entered library card number')

        email_input = self._find_element_by_xpath(
            xpath='//div[contains(.//span, "Adres poczty elektronicznej do korespondencji:")]//input[@type="text"]'
        )
        self.logger.debug('Found the input element for e mail address')
        email_input.send_keys(self._email_address)
        self.logger.info('Successfully entered email address')

        e_resource_checkbox = self._find_element_by_xpath(
            xpath=f'//div[contains(@data-value, "{self._e_resource_name.lower()}")]'
        )
        self.logger.debug('Found checkbox for e-resource type')
        e_resource_checkbox.click()
        self.logger.info(f'Selected e-resource type: {self._e_resource_name}')

        self.logger.info('Form successfully filled with data!')
        self._save_screenshot()

    def _send_form_and_validate(self):
        """
        Submit your form and check the response page. Save a screenshot.
        :return:
        """

        submit_button = self._find_element_by_xpath(
            xpath='//div[contains(.//span, "Prześlij") and contains(@role, "button")]'
        )
        submit_button.click()
        self._save_screenshot()
        self.logger.info('Form was submitted successfully!')
        # TODO: Validate

    def fill_form_and_send(self):
        """
        Function to be called. Wait until form is available on the website. Fill it with data and submit.
        :return:
        """

        self._go_to_site_if_available('https://www.rajska.info/aktualnosci')
        self._wait_until_form_is_available()
        self._go_to_form()
        self._fill_form()
        self._send_form_and_validate()
        self.driver.quit()


if __name__ == "__main__":
    resource_request_instance = RequestResourceAccess()
    resource_request_instance.fill_form_and_send()
