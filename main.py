from flask import Response

from request_resource_access import RequestResourceAccess
from Database.form_data import get_next_user_data
from logger import create_logger


def main(request):
    logger = create_logger(name='main', level='debug')
    logger.info('Start selenium app')

    resource_request_instance = RequestResourceAccess()
    resource_request_instance.wait_until_form_is_available()
    while True:
        try:
            user_data = get_next_user_data()
            logger.info(f'Filling form with data for user: {user_data['name']}')
            resource_request_instance.fill_form_and_send(user_data)
        except StopIteration:
            break

    response = Response()
    response.status_code = 200
    return response
