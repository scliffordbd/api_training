import logging

import bosdyn.client.util
import bosdyn.geometry
from bosdyn.api.graph_nav.area_callback_pb2 import BeginCallbackRequest, BeginCallbackResponse
from bosdyn.client.area_callback_region_handler_base import (AreaCallbackRegionHandlerBase,
                                                             PathBlocked)
from bosdyn.client.area_callback_service_runner import run_service
from bosdyn.client.area_callback_service_servicer import AreaCallbackServiceServicer
from bosdyn.client.area_callback_service_utils import AreaCallbackServiceConfig
from bosdyn.client.robot import Robot

_LOGGER = logging.getLogger(__name__)

# Constants related to timeout on waiting.
PAUSE_KEY = "pause"
PAUSE_NAME = "Time to wait"
PAUSE_DESCR = "Maximum time to wait before crossing."
PAUSE_FIELD_ORDER = 1 # This is the second field shown in the UI.
PAUSE_DURATION = 30.0  # Default time to wait for entities (seconds).
PAUSE_TIMEOUT = 50.0  # Maximum time to wait (seconds).

# Constants related to the path being blocked.
TIMEOUT_BEHAVIOR_KEY = "behavior_on_timeout"
TIMEOUT_BEHAVIOR_NAME = "Behavior on timeout"
TIMEOUT_BEHAVIOR_DESCR = "What to do when the timeout is reached & the door is still not open."
TIMEOUT_BEHAVIOR_FIELD_ORDER = 2  # This is the third field shown in the UI.
TIMEOUT_BEHAVIOR_OPTIONS = {
    "proceed": "Proceed through the door (even if not open)",
    "block": "Prevent Spot from entering the door"
}
TIMEOUT_BEHAVIOR_DEFAULT = TIMEOUT_BEHAVIOR_OPTIONS["proceed"]

class RFIDDoorOpeningHandler(AreaCallbackRegionHandlerBase):
    """An example AreaCallbackRegionHandler implementation which waits for user defined duration to pass through an RFID enabled door.
        Requires the Spot robot to be equipped with a corresponding RFID fob.
    """

    # Helper functions for handling custom action UI parameters.
    def reset_default_params(self):
        self.settings[PAUSE_KEY] = PAUSE_DURATION
        self.settings[TIMEOUT_BEHAVIOR_KEY] = TIMEOUT_BEHAVIOR_DEFAULT

    def parse_config(self, request):
        # Anything not specified in the request is set to the default value.
        self.reset_default_params()

        # Read values stored in custom_params.
        try:
            self.settings.update(self._config.parse_params(request.custom_params))
        except ValueError as e:
            # This will be more robustly handled by coercion helpers in upcoming SDK release.
            _LOGGER.error(f"Door opening callback received invalid params: {e}. Leaving settings at default values.")

        if not self.settings[PAUSE_KEY]:
            _LOGGER.info("Warning: pause duration is set to 0 seconds.")


    def __init__(self, config: AreaCallbackServiceConfig, robot: Robot):
        super().__init__(config, robot)
        # The following helper functions are called to set the default user parameters when initializing
        # the area callback.
        self.settings = {}
        self.reset_default_params()

        #### TO DO ####
        # Set the policies for the start & end of the Area Callback region

    def begin(self, request: BeginCallbackRequest) -> BeginCallbackResponse.Status:
        #### TO DO ####

        # Unpack and configure any configuration settings as needed
        return BeginCallbackResponse.STATUS_OK

    def run(self):
        #### TO DO ####
        # In order to send a robot command, the AreaCallback requires a lease. Use the appropriate
        # policy and helper function to wait until a lease is given to the callback.
        
        #### TO DO ####
        # Now that we have control of the robot, execute necessary behavior for the AreaCallback.
        # In this case, wait for user defined timeout period for the door to fully open to continue.

        #### TO DO ####
        # The callback is complete. Use the appropriate policy and helper function to have the robot
        # navigate through the region and give back control to the client (graph nav).

    def end(self):
        # No extra cleanup is required by this callback. For something like a callback that plays a
        # sound, this EndCallback call would be a place to stop playing the sound.
        pass


def update_area_callback_information(config):
    # Define custom parameter spec for action tablet UI.
    custom_specs = config.area_callback_information.custom_params.specs

    timeout_spec = custom_specs[PAUSE_KEY]
    timeout_spec.ui_info.display_name = PAUSE_NAME
    timeout_spec.ui_info.description = PAUSE_DESCR
    timeout_spec.ui_info.display_order = PAUSE_FIELD_ORDER
    timeout_spec.spec.double_spec.default_value.value = PAUSE_DURATION
    timeout_spec.spec.double_spec.min_value.value = 0
    timeout_spec.spec.double_spec.max_value.value = PAUSE_TIMEOUT
    timeout_spec.spec.double_spec.units.name = "seconds"

    timeout_behavior_spec = custom_specs[TIMEOUT_BEHAVIOR_KEY]
    timeout_behavior_spec.ui_info.display_name = TIMEOUT_BEHAVIOR_NAME
    timeout_behavior_spec.ui_info.description = TIMEOUT_BEHAVIOR_DESCR
    timeout_behavior_spec.ui_info.display_order = TIMEOUT_BEHAVIOR_FIELD_ORDER
    timeout_behavior_spec.spec.string_spec.options.ClearField()
    timeout_behavior_spec.spec.string_spec.options.extend(TIMEOUT_BEHAVIOR_OPTIONS.values())
    timeout_behavior_spec.spec.string_spec.default_value = TIMEOUT_BEHAVIOR_DEFAULT
    timeout_behavior_spec.spec.string_spec.editable = False  # The options are immutable.

def main():
    import argparse
    parser = argparse.ArgumentParser()
    bosdyn.client.util.add_base_arguments(parser)
    bosdyn.client.util.add_payload_credentials_arguments(parser)
    bosdyn.client.util.add_service_hosting_arguments(parser)
    options = parser.parse_args()
    bosdyn.client.util.setup_logging(options.verbose)

    self_ip = bosdyn.client.common.get_self_ip(options.hostname)

    # Initialize robot object and authenticate.
    sdk = bosdyn.client.create_standard_sdk('DoorOpeningService')
    robot = sdk.create_robot(options.hostname)
    robot.authenticate_from_payload_credentials(*bosdyn.client.util.get_guid_and_secret(options))
    robot.start_time_sync()
    robot.time_sync.wait_for_sync()

    # Configure the area callback service.
    # Don't call it 'door-opener'... That's what our arm door opening service is called.
    service_name = 'rfid-door-opener'
    required_lease_resources = ['body']
    config = AreaCallbackServiceConfig(service_name,
                                       required_lease_resources=required_lease_resources)
    # Specify custom parameters for user config.
    update_area_callback_information(config)
    servicer = AreaCallbackServiceServicer(robot, config, RFIDDoorOpeningHandler)

    # Run the area callback service.
    service_runner, keep_alive = run_service(robot, servicer, options.port, self_ip)
    with keep_alive:
        service_runner.run_until_interrupt()

if __name__ == '__main__':
    main()
