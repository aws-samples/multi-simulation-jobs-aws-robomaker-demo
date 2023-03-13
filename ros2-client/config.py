import time
import boto3
import os
import sys
from lxml import etree

"""
This is a Python script to set the Instance IP automatically generated by AWS RoboMaker 
to the XML in the docker containers in simulation job.
"""
# Required Value - AWS credentials
ACCESS_KEY = "Account's Access Key"
SECRET_KEY = "Account's Secret Access Key"
AWS_DEFAULT_REGION = "us-east-1"

# default setting - If you want to change, If you want to change this value, change the Dockerfile as well.
FASTRTPS_TEMPLATE = "/home/fastdds-client-default.xml"

client = boto3.client('robomaker',
                      aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY,
                      region_name=AWS_DEFAULT_REGION)


def set_test_env():
    # Fast DDS's configuration file path - It should be the same as the Dockerfile configuration information.
    FASTRTPS_DEFAULT_PROFILES_FILE = 'fastdds-client.xml'
    os.environ['FASTRTPS_DEFAULT_PROFILES_FILE'] = FASTRTPS_DEFAULT_PROFILES_FILE

    # Simulation Job's ARN - This value is automatically set when RoboMaker is run.
    AWS_ROBOMAKER_SIMULATION_JOB_ARN = "arn:aws:robomaker:us-east-1:012345678901:simulation-job/sim-g0959w53813w"
    os.environ['AWS_ROBOMAKER_SIMULATION_JOB_ARN'] = AWS_ROBOMAKER_SIMULATION_JOB_ARN


def check_pre_status(job_status):
    status_list = ['Pending', 'Preparing', 'Restarting']
    if job_status in list(status_list):
        print(f'current state is {job_status}')
        return True
    print(f'current state is {job_status}')
    return False


def set_host_ip_at_xml(xml_default_path, xml_file_path, host_ip_addr):
    tree = etree.parse(xml_default_path)
    root = tree.getroot()
    for profiles in root:
        name_space = {"fastdds": "http://www.eprosima.com/XMLSchemas/fastRTPS_Profiles"}
        wan_addr = profiles.find('fastdds:transport_descriptors', name_space) \
            .find('fastdds:transport_descriptor', name_space) \
            .find('fastdds:wan_addr', name_space)
        wan_addr.text = host_ip_addr
    tree.write(xml_file_path, encoding="utf-8", xml_declaration=True)


if __name__ == "__main__":
    # For local test
    #set_test_env()
    print(os.getenv('AWS_ROBOMAKER_SIMULATION_JOB_ARN'))
    status = 'Pending'
    while True:
        time.sleep(5)
        response = client.describe_simulation_job(job=os.getenv('AWS_ROBOMAKER_SIMULATION_JOB_ARN'))
        print(response)
        status = response['status']
        if check_pre_status(job_status=status):
            print(f'The simulation job is {status}... retry')
        else:
            break

    if status != 'Running':
        sys.exit(f'The simulation job is not working the status = {status}')

    host_ip_addr = response['networkInterface']['privateIpAddress']
    print(f'The simulation job is running on host_ip = {host_ip_addr}')
    set_host_ip_at_xml(FASTRTPS_TEMPLATE, os.getenv('FASTRTPS_DEFAULT_PROFILES_FILE'), host_ip_addr)
    print("FastDDS settings configured.")
