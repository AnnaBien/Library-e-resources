import functions_framework

from flask import Response

from cloud_run_container_delete import CloudRunContainerDelete, ContainerDeletionFailure


@functions_framework.http
def delete_container(*args):
    response = Response()
    cloud_run_handler_instance = CloudRunContainerDelete()
    try:
        cloud_run_handler_instance.delete_container()
        response.status_code = 200
        response.response = 'Container deleted'
    except ContainerDeletionFailure:
        response.status_code = 500
        response.response = 'Internal error; Container not deleted'
    return response
