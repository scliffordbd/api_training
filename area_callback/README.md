# RFID Door Opening Area Callback

This example will show the user how to create and run an area callback that allows a Spot robot to navigate an automatic RFID controlled door. It is based on the following door specs:

* Make/model of door opener: NABCO 'Pedestrian Door Operator' SN: 25011274
* Make/model of RFID sensor and fob: Nedap 'uPASS REACH REGION 2&3' SN:R127 F04 0195

This example can be approached at least two ways:
1. As an interactive exercise for the user to complete
2. As a runnable example

In either case, the code can be run locally or as a Spot Extension. See the Running the Example section of the readme for more information.

Please see the general [GraphNav Area Callback documentation](https://dev.bostondynamics.com/docs/concepts/autonomy/graphnav_area_callbacks) as well as the [Area Callback example](https://dev.bostondynamics.com/python/examples/area_callback/readme#area-callback-tutorial) for more information about what Area Callbacks are and how they work.

## Setup

Ensure that you have done the following setup steps:
* Mount the appropriate RFID fob on the robot you intend to deploy the area callback to.
* Attach a payload with a CORE I/O to the robot.
* Ensure your RFID door is set up and running as intended.

## Completing the Exercise

The [rfid_door_opening.py](rfid_door_opening.py) file contains TO DO sections where you must enter the appropriate lines of code in order to complete the functionality of the area callback. Please refer to the [rfid_door_opening_solution.py](rfid_door_opening_solution.py) and any other materials you may find useful as necessary.

## Running the Example

### Running Locally

To test that the door opening python code works, it is best to run it on the robot locally before deploying as a Spot Extension. To do so:

0. Ensure that your robot is properly configured per Setup and is turned on.
1. Connect your computer to the robot's network. The default address is 192.168.80.3.
3. Open a terminal session to the `area_callback` directory.
```sh
$ sudo ufw allow from <robot_IP> to any port <port>
```
4. You may need to open a port for the robot to communication with the service:

```sh
$ sudo ufw allow from <robot_IP> to any port <port>
```

5. Launch your area callback service by running:

```sh
$ python3 rfid_door_opening.py --port <port> <robot_IP>
```
or
```sh
$ python3 rfid_door_opening_solution.py --port <port> <robot_IP>
```
if you are using the solution file.

### Running as a Spot Extension

You can either go through the process to create a Spot Extension (detailed below), or upload the pre-loaded `rfid-door-opener.spx` file to the CORE I/O that utilizes the solution file. Either way, you should be familiar with the following files:
* Dockerfile.l4t
* docker-compose.yml
* manifest.json

Use the following steps to create a Spot Extension:

1. In a terminal window or an IDE, navigate to the `api_training/area_callback` directory.
2. Run the following command to build the docker image:

```sh
$ sudo docker build -t rfid-door-opener:l4t -f Dockerfile.l4t .
```

3. Save the docker image as a tar.gz file:

```sh
$ sudo docker save rfid-door-opener:l4t | pigz > rfid-door-opener.tar.gz
```
4. If you are using the `rfid_door_opening.py` file, you will need to update the appropriate lines in the `Dockerfile.l4t` file.

5. Package the docker image and all necessary files as an .spx extension:

```sh
$ tar -cvzf rfid-door-opener.spx rfid-door-opener.tar.gz docker-compose.yml manifest.json icon.png
```

#### Upload Spot Extension

1. Connect to the admin console for the CORE I/O you are working with. The default route is 192.168.80.3:21443 but you can also access it through the payloads page of the robot you are working with.
2. Upload the .spx file.
3. Vefify that your extension is running as intended by verifying that your action shows up under Area Callbacks in the Settings > Actions menu of the tablet.