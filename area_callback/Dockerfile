# This Dockerfile is used to test the area callback locally before creating a Spot Extension.
FROM python:3.10

# Install the API wheels and other requirements.
COPY docker-requirements.txt prebuilt/*.whl ./

RUN python3 -m pip install -r docker-requirements.txt --find-links .

COPY rfid_door_opening_solution.py /app/
WORKDIR /app

ENTRYPOINT ["python3", "/app/rfid_door_opening_solution.py"]
# Default arguments for running on the CORE I/O
CMD [ "192.168.50.3", "--payload-credentials-file=/opt/payload_credentials/payload_guid_and_secret"]

