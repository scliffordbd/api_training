import boto3
import io
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
import time
import urllib3

from bosdyn.scout.client import ScoutClient

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def save_jpg_image_local(image, filename):
    img = mpimg.imread(io.BytesIO(image), format='jpg')
    plt.imshow(img)
    plt.axis('off')  # Hide x and y axes
    plt.savefig(filename)
    # plt.show()


def save_raw_image_local(image, filename):
    # Assuming Spot CAM+IR Thermal image
    img = np.frombuffer(image, dtype='uint16')
    height = 512
    width = 640
    data = img.reshape((height, width))
    plt_image = list(data)
    plt.imshow(plt_image, plt.cm.inferno)
    plt.axis('off')  # Hide x and y axes
    plt.savefig(filename)
    # plt.show()


def get_image_from_scout(scout_client, filename):
    params = {'missionName':'ThermalMissionExportData'}
    # Get recent run captures
    run_captures_response = scout_client.get_run_captures(params=params)

    # Get and format the image url
    run_captures = run_captures_response.json()

    url = run_captures.get('resources')[0].get('dataUrl')
    full_url = f'https://{scout_client._hostname}{url}'.replace(' ', '%20')

    # Get the image response
    get_image_response = scout_client.get_image(full_url)

    # Create and save the image from the data in Scout
    image_data = get_image_response.data
    if url.endswith('.raw'):
        save_raw_image_local(image_data, filename)
    else:
        save_jpg_image_local(image_data, filename)


def upload_to_aws(source_filename, bucket_name, destination_filename):
    s3 = boto3.client('s3')
    s3.upload_file(source_filename, bucket_name, destination_filename)


def main():
    hostname = '10.202.101.3'  # Our Scout Instance
    bucket_name = 'export-data-training-bucket'  # My s3 bucket
    filename = f'export-data-{time.strftime("%Y%m%d-%H%M%S")}.jpg'

    scout_client = ScoutClient(hostname=hostname, verify=False)
    scout_client.authenticate_with_password()

    get_image_from_scout(scout_client, filename)
    upload_to_aws(filename, bucket_name, filename)


if __name__ == '__main__':
    main()
