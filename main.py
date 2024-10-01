import datetime

from os import path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class RequestResourceAccess:
    def __init__(self):
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        self.http_address = 'https://www.rajska.info/pobierz-kody-kolejne-platformy-czekaja'
        self.library_card = '<your_library_card_number>'
        self.email_address = '<your_email_address>'
        self.e_resource_name = 'legimi'  # legimi or empik
        self.screenshot_path = '<path>'

    def go_to_form(self):
        """
        Go to Rajska library website and find the form to request e-resources.
        Note: Form opens in a new tab

        :return: None
        """

        self.driver.get(self.http_address)
        current_window = self.driver.current_window_handle
        href_elem = self.driver.find_element(by=By.LINK_TEXT, value='formularz zgłoszeniowy')
        href_elem.click()
        for window in self.driver.window_handles:
            if window != current_window:
                self.driver.switch_to.window(window)
                break

    def fill_form(self, save_screenshot=True):
        """
        Fill form:
            - your library card number
            - your e-mail address to which an access code will be sent
            - the e-resource type: legimi or empik

        Save a screenshot of the filled form.
        :return: None
        """

        card_no_input = self.driver.find_element(
            by=By.XPATH,
            value='//div[contains(.//span, "Numer karty czytelnika WBP w Krakowie:")]//input[@type="text"]'
        )
        card_no_input.send_keys(self.library_card)

        email_input = self.driver.find_element(
            by=By.XPATH,
            value='//div[contains(.//span, "Adres poczty elektronicznej do korespondencji:")]//input[@type="text"]'
        )
        email_input.send_keys(self.email_address)

        e_resource_checkbox = self.driver.find_element(
            by=By.XPATH,
            value=f'//div[contains(@data-value, "{self.e_resource_name.lower()}")]'
        )
        e_resource_checkbox.click()
        if save_screenshot:
            self.driver.save_screenshot(
                filename=path.join(self.screenshot_path, f'filled_form_{datetime.datetime.now()}.png')
            )

    def send_form_and_validate(self, save_screenshot=True):
        """
        Submit your form, save a screenshot of response page and check whether the confirmation
        message is present.
        :return:
        """

        submit_button = self.driver.find_element(
            by=By.XPATH,
            value='//div[contains(.//span, "Prześlij") and contains(@role, "button")]'
        )
        submit_button.click()
        if save_screenshot:
            self.driver.save_screenshot(
                filename=path.join(self.screenshot_path, f'form_response_{datetime.datetime.now()}.png')
            )
        confirmation_msg = self.driver.find_element(
            by=By.XPATH,
            value='//div[contains(., "Twoja odpowiedź została zapisana.")]'
        )
        # TODO: Send an email with result

    def fill_form_and_send(self):
        self.go_to_form()
        self.fill_form()
        self.send_form_and_validate()

    def wait_until_form_is_available(self):
        pass    # TODO


if __name__ == "__main__":
    obj = RequestResourceAccess()
    obj.wait_until_form_is_available()
    obj.fill_form_and_send()
