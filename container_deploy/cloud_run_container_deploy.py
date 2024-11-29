from google.cloud import run_v2
from google.iam.v1.policy_pb2 import Policy
from google.iam.v1.policy_pb2 import Binding

from logger import create_logger


class ContainerDeploymentFailure(Exception):
    def __init__(self):
        self.logger = create_logger(name=self.__class__.__name__, level='error')
        self.logger.exception('Could not deploy a standalone-chrome container')


class CloudRunContainerDeploy:

    def __init__(self):
        self.client = run_v2.ServicesClient()
        self.parent = 'projects/e-resources-rajska/locations/europe-central2'
        self.logger = create_logger(self.__class__.__name__, level='debug')

    @staticmethod
    def get_container_template():
        return run_v2.Container(
                {
                    'image': 'europe-central2-docker.pkg.dev/e-resources-rajska/docker-images/standalone-chrome',
                    'ports': [{"container_port": 4444}],
                    'resources': {
                        'limits': {
                            'memory': '2Gi'
                        }
                    }
                }
            )

    def allow_unauthenticated_requests(self):
        """
        Grant unauthenticated access to container.
        :return: None
        """

        policy_binding = Policy(bindings=[
            Binding(
                role="roles/run.invoker",
                members=["allUsers"]
            )
        ])
        policy = self.client.set_iam_policy(
            {
                'resource': f'{self.parent}/services/standalone-chrome',
                'policy': policy_binding
            }
        )
        self.logger.info(f'Authentication policy set for container: {policy}')

    def deploy_container(self):
        """
        Configure and deploy standalone-chrome container with restricted access by default.
        :return: None
        """

        service = run_v2.Service()
        service.template.containers = [self.get_container_template()]
        service.ingress = 'INGRESS_TRAFFIC_ALL'
        request = run_v2.CreateServiceRequest(
            {
                'parent': self.parent,
                'service': service,
                'service_id': 'standalone-chrome'
            }
        )
        try:
            operation = self.client.create_service(request=request)
            response = operation.result()
            self.logger.debug(f'Operation deploy container response: {response}')
        except Exception as service_failure:
            raise ContainerDeploymentFailure from service_failure
