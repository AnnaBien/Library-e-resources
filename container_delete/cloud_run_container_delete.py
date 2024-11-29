from google.cloud import run_v2

from logger import create_logger


class ContainerDeletionFailure(Exception):
    def __init__(self):
        self.logger = create_logger(name=self.__class__.__name__, level='error')
        self.logger.exception('Could not delete a standalone-chrome container')


class CloudRunContainerDelete:

    def __init__(self):
        self.client = run_v2.ServicesClient()
        self.service_path = f'projects/e-resources-rajska/locations/europe-central2/services/standalone-chrome'
        self.logger = create_logger(self.__class__.__name__, level='debug')

    def delete_container(self):
        try:
            operation = self.client.delete_service(name=self.service_path)
            response = operation.result()
            self.logger.debug(f'Operation delete container response: {response}')
        except Exception as service_failure:
            raise ContainerDeletionFailure from service_failure
