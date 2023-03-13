## Multi simulation jobs in AWS RoboMaker Demo

---
The demo was configured to enable communication between ROS2 applications deployed in AWS RoboMaker's multiple simulation jobs.     
This is a demo of setting up a Docker container format Talker and Listener to do TCP communication through [Fast DDS Discovery Server](https://fast-dds.docs.eprosima.com/en/latest/fastdds/discovery/discovery_server.html#discovery-server).    
This source code provides a setting template that can be used when you want to communicate and work with multiple simulation jobs simultaneously using AWS RoboMaker.   
Using [AWS RoboMaker](https://docs.aws.amazon.com/robomaker/latest/dg/chapter-welcome.html), which operates in a separate isolated host container, communication between ROS2 robot applications is supported, and Fast DDS discovery server and TCP transport layer settings are templated to run simulations.   

![architecture.png](/docs/architecture.png)

## Requirements

---

### AWS Account
-  Depending on usage of the service, charges may be charged to the customer's account. 
### AWS RoboMaker's Quota Increase
- In order to increase the quota, there must be clear usage requirements.
- You will need 2 or more to run this demo.

## Get Started
This demo was created using the ROS2 foxy demo library.

---
### 1. Setup Development Environment
#### 1) Install Docker.
```bash
sudo apt update & sudo apt install -y docker.io
sudo usermod -aG docker ubuntu
```
#### 2) Install AWS CLI.
```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

#### 3) Install with CloudFormation Stack.
This template includes the tasks below.

(1) Create VPC

In this [Create VPC](https://us-east-1.console.aws.amazon.com/vpc/home?region=us-east-1#CreateVpc:createMode=vpcWithResources), you create VPCs, Subnets, Security Groups, and more.   
In this VPC, Discovery Server and RoboMaker Simulation jobs are set up so that they can run.

In [Security Group](https://us-east-1.console.aws.amazon.com/vpc/home?region=us-east-1#SecurityGroups), set an inbound rule for the Security Group to be used in the VPC created above.
Modify the Rule to allow all traffic within the VPC.

(2) Create Amazon EC2 Instance for Discovery Server in the VPC created step 1.
Create EC2 instance and install [Fast DDS](https://fast-dds.docs.eprosima.com/en/latest/fastdds/discovery/discovery_server.html#discovery-server) latest version.

(3) Set Amazon EC2 Instance for Discovery Server's private IP at the discovery-server.xml configuration.
Apply the private IP of the corresponding EC2 instance to `<wan_addr>` and `<wan_address>` in discovery-server.xml and execute the command below.

(4) Create a role to set when executing RoboMaker simulation.

Run the CloudFormation template by executing the command below.
```bash
cd discovery-server
```
```bash
aws cloudformation create-stack --stack-name DiscoveryServerStack --template-body file://fastdds-discovery-server-cfn.yaml --capabilities CAPABILITY_IAM
```
You will get the following result.

```json
{
    "StackId": "arn:aws:cloudformation:us-east-1:[your account ID]:stack/DiscoveryServerStack/xxxxxx-xxx-xxxx-xxxx-xxxxxx"
}
```

Query the status of the executed CloudFormation Stack.

```bash
aws cloudformation describe-stacks --stack-name DiscoveryServerStack 
```
You will get the following result. Check the outputs when "Stack Status" becomes "CREATE COMPLETE".
```bash
{
    "Stacks": [
        {
            "StackId": "arn:aws:cloudformation:us-east-1:012345678901:stack/DiscoveryServerStack/0c5647d0-bee6-11ed-aaa2-12f41fa9589d",
            "StackName": "DiscoveryServerStack",
            "Description": "This template deploys a VPC in either us-east-1 or us-west-2, with a pair of public and private subnets spread across two Availability Zones. It deploys an internet gateway, with a default route on the public subnets, a Linux t2.micro Instance with Security Group with setup FastDDS",
            "CreationTime": "2023-03-10T01:51:17.861000+00:00",
            "RollbackConfiguration": {},
            "StackStatus": "CREATE_COMPLETE",
            "DisableRollback": false,
            "NotificationARNs": [],
            "Capabilities": [
                "CAPABILITY_IAM"
            ],
            "Outputs": [
                {
                    "OutputKey": "PublicIp",
                    "OutputValue": "XXX.XXX.XXX.XXX",
                    "Description": "EC2 Instance Public Ip"
                },
                {
                    "OutputKey": "PrivateIp",
                    "OutputValue": "10.0.1.1",
                    "Description": "EC2 Instance Private Ip"
                },
                {
                    "OutputKey": "RoboMakerSimulationRoleArn",
                    "OutputValue": "arn:aws:iam::012345678901:role/DiscoveryServerStack1-RoboMakerSimulationRole-3AKMGYLPN4IK"
                },
                {
                    "OutputKey": "PublicSubnet2",
                    "OutputValue": "subnet-0b113574e06f05af8",
                    "Description": "RoboMaker Public subnet 2"
                },
                {
                    "OutputKey": "SecurityGroup",
                    "OutputValue": "sg-080c16a0396099ab5",
                    "Description": "RoboMaker SecurityGroup"
                },
                {
                    "OutputKey": "PublicSubnet1",
                    "OutputValue": "subnet-0550b83f3542793e2",
                    "Description": "RoboMaker Public subnet 1"
                }
            ],
            "Tags": [],
            "EnableTerminationProtection": false,
            "DriftInformation": {
                "StackDriftStatus": "NOT_CHECKED"
            }
        }
    ]
}
```
Apply the PrivateIp value from Output to the discovery server IP value (e.g. 10.0.1.1) in Dockerfile and fastdds-client.xml file.
This value is different each time you run CloudFormation.

Apply to line 59 of the Dockerfile.

```bash
export ROS_DISCOVERY_SERVER=\"10.0.1.1:9843\" \n\
```

Apply to line 31 of fastdds-client.xml.

```xml
...
                        <discoveryServersList>
                            <RemoteServer prefix="44.53.00.5f.45.50.52.4f.53.49.4d.41"> <!-- must match server's id -->
                                <metatrafficUnicastLocatorList>
                                    <locator>
                                        <tcpv4> <!-- must match server's (ip, port) -->
                                            <address>10.0.1.1</address>
                                            <port>64863</port>
                                            <physical_port>9843</physical_port>
                                        </tcpv4>
                                    </locator>
                                </metatrafficUnicastLocatorList>
                            </RemoteServer>
                        </discoveryServersList>
...
```


### 2. Start discovery server
Connect to the launched EC2 instance and run the discovery server as shown below.

```bash
source /home/ubuntu/Fast-DDS/install/setup.bash
fastdds discovery -i 0 -x discovery-server.xml 
```

You will get the following result.
```bash
### Server is running ###
  Participant Type:   SERVER
  Server ID:          0
  Server GUID prefix: 44.53.00.5f.45.50.52.4f.53.49.4d.41
  Server Addresses:   TCPv4:[0.0.0.0]:4250871411
```



### 3. Dockerize Images & Upload Images to Amazon ECR
In this step, create a Docker Image to be applied to the Robot Application, upload it, and use it.   
In Step 6 at the bottom, a method of using Simulation Application using xml with other port information applied is added.   
The reason for dividing the two settings is to prevent ports from overlapping because Simulation Job is executed in one instance in the form of Robot Application + Simulation Application.    
Please take note of this and apply it.
```bash
cd ros2-client
```

#### 1) Enter the aws credentials information into config.py.

```bash
aws sts get-session-token
```

```python
# Required Value - AWS credentials
ACCESS_KEY = "Account's Access Key"
SECRET_KEY = "Account's Secret Access Key"
SESSION_TOKEN = "Account's Session Token"
```

#### 2) Create ECR Repository name as `demo-robot-app`.

```bash
aws ecr create-repository \
    --repository-name demo-robot-app \
    --image-scanning-configuration scanOnPush=true \
    --region us-east-1
```

Use the following steps to authenticate and push an image to your repository.     
For additional registry authentication methods, including the Amazon ECR credential helper, see [Registry Authentication](https://docs.aws.amazon.com/AmazonECR/latest/userguide/Registries.html).

(1) Retrieve an authentication token and authenticate your Docker client to your registry.
```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <ACCOUNT>.dkr.ecr.<REGION>.amazonaws.com
```
(2) Build your Docker image using the following command. For information on building a Docker file from scratch see the instructions here . You can skip this step if your image is already built:
```bash
cd ros2-client
docker build -t demo-robot-app .
```
(3) After the build completes, tag your image, so you can push the image to this repository:
```bash
docker tag demo-robot-app:latest <ACCOUNT>.dkr.ecr.<REGION>amazonaws.com/demo-robot-app:latest
```
(4) Run the following command to push this image to your newly created AWS repository:
```bash
docker push <ACCOUNT>.dkr.ecr.<REGION>.amazonaws.com/demo-robot-app:latest
```

### 4. Create AWS RoboMaker's Robot application
Register the built ECR image as a robot application in AWS RoboMaker.
```bash
aws robomaker create-robot-application \ 
--name demo-robot-app \ 
--robot-software-suite name=General \ 
--environment uri=<ACCOUNT>.dkr.ecr.<REGION>.amazonaws.com/demo-robot-app:latest                       
```
You will get the following result.
```bash
{
    "arn": "arn:aws:robomaker:us-east-1:012345678901:robot-application/demo-robot-app/1678415094831",
    "name": "demo-robot-app",
    "version": "$LATEST",
    "robotSoftwareSuite": {
        "name": "General"
    },
    "lastUpdatedAt": "2023-03-10T02:24:54+00:00",
    "revisionId": "7fc17390-3f26-4b2e-92f5-73bc0fc06fa6",
    "tags": {},
    "environment": {
        "uri": "012345678901.dkr.ecr.us-east-1.amazonaws.com/demo-robot-app:latest"
    }
}
```

### 5. Create a Simulation Job Batch

You must change the settings below in the template xml file to match the values created for your account.
- `createSimulationJobRequests.iamRole`: RoboMaker's Simulation Job Batch role. Use RoboMakerSimulationRoleArn value in CloudFormation output.
- `createSimulationJobRequests.robotApplications.application`: Robot Application's ARN value that you created step 4.
- `createSimulationJobRequests.vpcConfig.subnets`: VPC's Subnets. 2 or more are required. Use public subnet1, 2 value in CloudFormation output.
- `createSimulationJobRequests.vpcConfig.securityGroups`: VPC's Security Group name. Use SecurityGroup value in CloudFormation output.

```bash
aws robomaker start-simulation-job-batch --cli-input-json  file://simulation_job_batch.json --region us-east-1
```

If you look at the CloudWatch log of the listener application in the [Simulation Job](https://us-east-1.console.aws.amazon.com/robomaker/home?region=us-east-1#simulationJobs), you can see that messages from talker application in other Simulation Jobs are received as shown below.

![result.png](/docs/result.png)



### 6. Using Simulation application (Optional)
Run the command below to use 2 containers in one simulation job.
This Dockerfile uses fastdds-client-sim.xml with different assigned ports (e.g. 49154), so be careful with the settings.
```bash
docker build -t demo-sim-app . -f Dockerfile-sim
```

```bash
aws robomaker create-simulation-application --name my-sim-app --simulation-software-suite name=SimulationRuntime  --robot-software-suite name=General --environment uri=<ACCOUNT>.dkr.ecr.<REGION>.amazonaws.com/demo-sim-app:latest
```

## References

---

- FastDDS: https://fast-dds.docs.eprosima.com/en/latest/index.html
- AWS RoboMaker: https://docs.aws.amazon.com/robomaker/latest/dg/chapter-welcome.html
- Amazon ECR: https://docs.aws.amazon.com/AmazonECR/latest/userguide/what-is-ecr.html
- ROS2 foxy: https://docs.ros.org/en/foxy/Installation/DDS-Implementations/Working-with-eProsima-Fast-DDS.html


## Security

---

See [CONTRIBUTING](docs/CONTRIBUTING.md#security-issue-notifications) for more information.

## License

---

This library is licensed under the MIT-0 License. See the LICENSE file.

