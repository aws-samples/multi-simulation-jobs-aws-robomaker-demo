import json
from lxml import etree
import requests  # pip install requests

"""
This is a Python script to set the Instance private IP in FastDDS Discovery Server configuration xml file.
"""


def set_host_ip_at_xml(xml_default_path, xml_file_path, host_ip_addr):
    tree = etree.parse(xml_default_path)
    root = tree.getroot()
    for profiles in root:
        name_space = {"fastdds": "http://www.eprosima.com/XMLSchemas/fastRTPS_Profiles"}
        wan_addr = profiles.find('fastdds:transport_descriptors', name_space) \
            .find('fastdds:transport_descriptor', name_space) \
            .find('fastdds:wan_addr', name_space)
        wan_addr.text = host_ip_addr

        wan_address = profiles.find('fastdds:participant', name_space) \
            .find('fastdds:rtps', name_space) \
            .find('fastdds:builtin', name_space) \
            .find('fastdds:metatrafficUnicastLocatorList', name_space) \
            .find('fastdds:locator', name_space) \
            .find('fastdds:tcpv4', name_space) \
            .find('fastdds:wan_address', name_space)
        wan_address.text = host_ip_addr
    tree.write(xml_file_path, encoding="utf-8", xml_declaration=True)


if __name__ == "__main__":
    FASTRTPS_DS_TEMPLATE = "discovery-server.xml"
    r = requests.get('http://169.254.169.254/latest/dynamic/instance-identity/document')
    instance_details = json.loads(r.text)
    host_ip_addr = instance_details['privateIp']
    print(f"The discovery server instance's private IP is {host_ip_addr}")
    set_host_ip_at_xml(FASTRTPS_DS_TEMPLATE, FASTRTPS_DS_TEMPLATE, host_ip_addr)
    print("FastDDS Discovery Server settings configured.")
