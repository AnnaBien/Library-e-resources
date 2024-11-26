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
        self.logger = create_logger(self.__class__.__name__, level='debug')
        self.library_url = 'https://www.rajska.info/aktualnosci'
        self.driver = webdriver.Remote(command_executor='<standalone-chrome-container-address>', options=Options())

    def save_screenshot(self):
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

    def _go_to_site_if_available(self, site_address):
        """
        Go to library site and check if it contains an error (POST response is still 200).
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

    def wait_until_form_is_available(self, counter: int = 1, duration: int = 5):
        """
        Wait until the form becomes available on the library website.

        :param counter: Number of repetitions of the check
        :param duration: Time duration between repetitions [s]
        :return:
        """

        self._go_to_site_if_available('https://www.rajska.info/aktualnosci')
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

    def _fill_form(self, form_data):
        """
        Fill form with:
            - your library card number
            - your e-mail address to which an access code will be sent
            - the e-resource type: legimi or empik

        Save a screenshot of the filled form.
        Note: This function must be preceded by go_to_form().
        :param form_data: (dict) {'library_card_no': ..., 'email': ..., 'resource_type': ...}
        :return: None
        """

        card_no_input = self._find_element_by_xpath(
            xpath='//div[contains(.//span, "Numer karty czytelnika WBP w Krakowie:")]//input[@type="text"]'
        )
        self.logger.debug('Found the input element for the library card number')
        card_no_input.send_keys(form_data['library_card_no'])
        self.logger.info('Successfully entered library card number')

        email_input = self._find_element_by_xpath(
            xpath='//div[contains(.//span, "Adres poczty elektronicznej do korespondencji:")]//input[@type="text"]'
        )
        self.logger.debug('Found the input element for e mail address')
        email_input.send_keys(form_data['email'])
        self.logger.info('Successfully entered email address')

        e_resource_checkbox = self._find_element_by_xpath(
            xpath=f'//div[contains(@data-value, "{form_data['resource_type']}")]'
        )
        self.logger.debug('Found checkbox for e-resource type')
        e_resource_checkbox.click()
        self.logger.info(f'Selected e-resource type: {form_data['resource_type']}')

        self.logger.info('Form successfully filled with data!')
        self.save_screenshot()

    def _submit_form(self):
        """
        Submit your form and save a screenshot of the response page.
        :return:
        """

        submit_button = self._find_element_by_xpath(
            xpath='//div[contains(.//span, "Prześlij") and contains(@role, "button")]'
        )
        submit_button.click()
        self.save_screenshot()
        self.logger.info('Form was submitted successfully!')

    def fill_form_and_send(self, form_data):
        """
        Can be executed only if form is available at the library website.
        Performs all actions to fill the form and submit it with data of a single user.
        :return:
        """

        self._go_to_form()
        self._fill_form(form_data)
        self._submit_form()
