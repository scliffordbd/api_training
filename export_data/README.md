# ExportData

Holds code used in the export data course.

- [Spot Exercise](./spot_export_data.ipynb)
- [Spot Exercise](./scout_export_data.ipynb)
- [Spot Exercise Answers](./answer/spot_export_data_answers.ipynb)
- [Scout Exercise Answers](./answer/scout_export_data_answers.ipynb)
- [Spot Examples](./example/Spot)
- [Scout Examples](./example/Scout)

## Setup Dependencies

See the requirements.txt file for a list of python dependencies which can be installed with pip using the command:

```
python3 -m pip install -r requirements.txt
```

## Exercises

Exercises use Jupyter notebooks. You can simply run the cells in the Jupyter notebook to run the code.

## Examples

Each command below assumes you are in the directory where the example is.

### Spot Example - Download Once

```
python3 download_once.py ROBOT_IP
```

### Spot Example - Download on Interval

```
python3 download_on_interval.py ROBOT_IP
```

### Spot Example - Post Mission Callback

Get your HOST_IP

```
python3 -m bosdyn.client ROBOT_IP self-ip
```

Run the example

```
python3 download_data_post_mission_callback.py --host-ip HOST_IP --port PORT ROBOT_IP
```

Create an Action in the Spot App. Spot > Menu > Settings > Actions > Create New Action.

Use the following:
- Template Action: Empty Inspection
- Name: Export Data
- Robot Body Control: No Control

Then, record a mission. On playback, choose this action as the Post Mission Callback. You must have an CORE to use the Post Mission Callback.

Alternatively, you could add this action to the end of your mission.

If you are having an issue loading your mission, it may be because of a firewall issue. Make sure the firewall is open. On Linux:

```
sudo ufw allow from {ROBOT_IP} to any port {PORT}
```

For example:

```
sudo ufw allow from 192.168.80.3 to any port 52003
```

Scout Example:

```
python3 export_data_to_s3_demo.py
```
