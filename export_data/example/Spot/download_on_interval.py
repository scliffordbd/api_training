import time

import bosdyn.client
import bosdyn.client.util
from bosdyn.client.data_acquisition_helpers import (download_data_REST, make_time_query_params)

HOSTNAME = '192.168.80.3'
DESTINATION_FOLDER = '.'
SECONDS = 1

def main():
    sdk = bosdyn.client.create_standard_sdk('DownloadDataOnce')
    robot = sdk.create_robot(HOSTNAME)
    bosdyn.client.util.authenticate(robot)
    robot.time_sync.wait_for_sync()

    start_time = time.time()
    while True:
        time.sleep(10)
        end_time = time.time()
        query_params = make_time_query_params(start_time, end_time, robot)

        download_data_REST(query_params, HOSTNAME, robot.user_token, destination_folder=DESTINATION_FOLDER)
        start_time = end_time


if __name__ == '__main__':
    main()