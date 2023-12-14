import argparse
import boto3
import logging
import os
import time

import bosdyn.client
import bosdyn.client.util
from bosdyn.api import service_customization_pb2
from bosdyn.api.mission import remote_pb2, remote_service_pb2_grpc
from bosdyn.client.data_acquisition_helpers import (download_data_REST, make_time_query_params,
                                                    make_time_query_params_from_group_name)
from bosdyn.client.directory_registration import (DirectoryRegistrationClient,
                                                  DirectoryRegistrationKeepAlive)
from bosdyn.client.server_util import GrpcServiceRunner, ResponseContext
from bosdyn.client.util import setup_logging

DIRECTORY_NAME = 'export-data-spot-example'
AUTHORITY = 'remote-mission'
SERVICE_TYPE = 'bosdyn.api.mission.RemoteMissionService'

_LOGGER = logging.getLogger(__name__)


class DaqDockingUploadServicer(remote_service_pb2_grpc.RemoteMissionServiceServicer):
    """
    When run, exports data from last mission. It will then send the data to an S3 bucket.
    Should be used in Post Mission Callback.
    """

    def __init__(self, bosdyn_sdk_robot, options, logger=None):
        self.logger = logger or _LOGGER
        self.bosdyn_sdk_robot = bosdyn_sdk_robot
        self.options = options
        self.destination_folder = options.destination_folder
        self.bucket = options.bucket
        self.seconds = options.seconds
        # No custom parameters
        self.custom_params = service_customization_pb2.DictParam.Spec()
        
    def EstablishSession(self, request, context):
        response = remote_pb2.EstablishSessionResponse()
        with ResponseContext(response, request):
            response.status = remote_pb2.EstablishSessionResponse.STATUS_OK
        return response
    
    def Tick(self, request, context):
        response = remote_pb2.TickResponse()
        with ResponseContext(response, request):
        
            # Set the Query Params
            query_params = None
            try:
                current_time = time.time()
                # current_time - 600 seconds means that we need an action to have run in the last 10 minutes
                query_params = make_time_query_params(current_time - self.seconds, current_time, robot)
            except ValueError as val_err:
                self.logger.error(f'Value Exception:\n{val_err}')
            
            # Download the data
            retry = 0
            success = False
            while not success and retry < 10:
                images = daq_store_client.list_stored_images(query_params)
                if len(images) > 0:
                    # Get the group_name from one of the actions we found
                    group_name = images[0].action_id.group_name
                    group_query_params = make_time_query_params_from_group_name(group_name, daq_store_client)
                    success = download_data_REST(group_query_params, options.hostname, robot.user_token,
                                destination_folder=self.destination_folder)
                retry += 1
            
            # Send the data to AWS
            if success and options.bucket:
                self.upload_to_aws(os.path.join(self.destination_folder, 'REST'))

        response.status = remote_pb2.TickResponse.STATUS_SUCCESS
        return response

    def Stop(self, request, context):
        response = remote_pb2.StopResponse()
        with ResponseContext(response, request):
            response.status = remote_pb2.StopResponse.STATUS_OK
        return response

    def TeardownSession(self, request, context):
        response = remote_pb2.TeardownSessionResponse()
        with ResponseContext(response, request):
            response.status = remote_pb2.TeardownSessionResponse.STATUS_OK
        return response
    
    def GetRemoteMissionServiceInfo(self, request, context):
        response = remote_pb2.GetRemoteMissionServiceInfoResponse()
        with ResponseContext(response, request):
            response.custom_params.CopyFrom(self.custom_params)
        return response
    
    def upload_to_aws(self, directory):
        s3 = boto3.client('s3')
        for filename in os.listdir(directory):
            try:
                f = os.path.join(directory, filename)
                s3.upload_file(f, self.bucket_name, filename)
            except IOError:
                self.logger.info(f'The file {f} was not found.')
            except Exception as e:
                self.logger.info(f'Exception in uploading file {f} to AWS.')


def run_service(bosdyn_sdk_robot, options, logger=None):
    add_servicer_to_server_fn = remote_service_pb2_grpc.add_RemoteMissionServiceServicer_to_server

    service_servicer = DaqDockingUploadServicer(bosdyn_sdk_robot, options, logger=logger)
    return GrpcServiceRunner(service_servicer, add_servicer_to_server_fn, options.port,
                             logger=logger)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    bosdyn.client.util.add_base_arguments(parser)
    bosdyn.client.util.add_service_endpoint_arguments(parser)
    parser.add_argument('--bucket', help=('S3 bucket to send data'))
    parser.add_argument('--destination-folder', help=('The folder to save the acquired data'),
                        required=False, default='.')
    parser.add_argument('--seconds', help=('The time to retrieve a recent action in a mission in seconds.'),
                        required=False, default=600, type=int)
    options = parser.parse_args()

    # Setup logging to use either INFO level or DEBUG level.
    setup_logging(options.verbose)

    sdk = bosdyn.client.create_standard_sdk('ExportDataAfterMissionSDK')
    robot = sdk.create_robot(options.hostname)
    bosdyn.client.util.authenticate(robot)
    robot.time_sync.wait_for_sync()
    daq_store_client = robot.ensure_client(
            bosdyn.client.data_acquisition_store.DataAcquisitionStoreClient.default_service_name)
    
    # Create a service runner to start and maintain the service on background thread.
    service_runner = run_service(robot, options, logger=_LOGGER)

    # Use a keep alive to register the service with the robot directory.
    dir_reg_client = robot.ensure_client(DirectoryRegistrationClient.default_service_name)
    keep_alive = DirectoryRegistrationKeepAlive(dir_reg_client, logger=_LOGGER)
    keep_alive.start(DIRECTORY_NAME, SERVICE_TYPE, AUTHORITY, options.host_ip, service_runner.port)

    # Attach the keep alive to the service runner and run until a SIGINT is received.
    with keep_alive:
        service_runner.run_until_interrupt()
        