import functions_framework

from flask import Response

from request_resource_access import RequestResourceAccess, RequestNotSend
from form_data import get_next_user_data
from logger import create_logger


@functions_framework.http
def selenium_client(*args):
    logger = create_logger(name='main', level='debug')
    logger.info('Start the Selenium Application')
    response = Response()
    resource_request_instance = RequestResourceAccess()
    try:
        resource_request_instance.wait_until_form_is_available()
        while True:
            try:
                user_data = get_next_user_data()
                logger.info(f'Filling out form with user data: {user_data['name']}')
                resource_request_instance.fill_form_and_send(user_data)
            except StopIteration:
                break
        response.status_code = 200
        response.response = 'Form submitted successfully.'
    except RequestNotSend:
        response.status_code = 500
        response.response = ('The Selenium application did not submit the form. '
                             'The form is unavailable or internal error occured.')
    return response
