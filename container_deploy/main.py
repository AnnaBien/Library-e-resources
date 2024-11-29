import functions_framework

from flask import Response
from cloud_run_container_deploy import CloudRunContainerDeploy, ContainerDeploymentFailure


@functions_framework.http
def deploy_and_configure_container(*args):
    response = Response()
    cloud_run_handler_instance = CloudRunContainerDeploy()
    try:
        cloud_run_handler_instance.deploy_container()
        cloud_run_handler_instance.allow_unauthenticated_requests()
        response.status_code = 200
        response.response = 'Container deployed'
    except ContainerDeploymentFailure:
        response.status_code = 500
        response.response = 'Internal error; Container not deployed'
    return response
