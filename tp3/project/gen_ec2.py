import boto3, time, json

with open('vpc_infos.json', 'r', encoding='utf-8') as file:
    infos = json.loads(file.read())

VPC_ID = infos['vpc_id']
SUBNET_PUB_ID = infos['subnet_pub_id']
SUBNET_PRI_ID = infos['subnet_priv_id']
SECURITY_PUB_ID = infos['security_group_pub_id']
SECURITY_PRI_ID = infos['security_group_priv_id']

def create_ec2_instance(ec2, image_id, instance_type, security_group_id, subnet_id, AssociatePublicIpAddress = False):
    response = ec2.run_instances(
        ImageId=image_id,
        InstanceType=instance_type,
        KeyName='vockey',
        MaxCount=1,
        MinCount=1,
        NetworkInterfaces=[
            {
                'AssociatePublicIpAddress': AssociatePublicIpAddress,
                'DeviceIndex': 0,
                'Groups': [ security_group_id ],
                'SubnetId' : subnet_id
            }
        ]
    )

    instance_id = response['Instances'][0]['InstanceId']
    print(f'EC2 instance created with ID: {instance_id}')

    return response['Instances'][0]

def wait_for_instance_state(ec2, instance_id, desired_state='running', interval=5, max_attempts=30):
    attempts = 0
    while attempts < max_attempts:
        try:
            response = ec2.describe_instances(InstanceIds=[instance_id])
            
            instance_state = response['Reservations'][0]['Instances'][0]['State']['Name']
            if instance_state == desired_state:
                print(f'EC2 Instance {instance_id} is ready')
                return True
                
            print(f'Waiting for EC2 Instance {instance_id} (State: {instance_state})')
        except Exception as e:
            print(f'Error: {str(e)}')
            
        time.sleep(interval)
        attempts += 1

    print(f'Timed out waiting for instance {instance_id} to reach the desired state.')
    return False


##########

ec2 = boto3.client('ec2', region_name='us-east-1')

serveurweb_instance = create_ec2_instance(ec2, 'ami-00beae93a2d981137', 't3.medium', SECURITY_PUB_ID, SUBNET_PUB_ID, True)
serveurweb_instance_id = serveurweb_instance['InstanceId']

serveurbdd_instance = create_ec2_instance(ec2, 'ami-00beae93a2d981137', 't2.micro', SECURITY_PRI_ID, SUBNET_PRI_ID, False)
serveurbdd_instance_id = serveurbdd_instance['InstanceId']

serveurmir_instance = create_ec2_instance(ec2, 'ami-04b70fa74e45c3917', 't2.micro', SECURITY_PRI_ID, SUBNET_PRI_ID, False)
serveurmir_instance_id = serveurmir_instance['InstanceId']

wait_for_instance_state(ec2, serveurweb_instance_id)
wait_for_instance_state(ec2, serveurbdd_instance_id)
wait_for_instance_state(ec2, serveurmir_instance_id)

response = ec2.describe_instances(InstanceIds=[serveurweb_instance_id])
hostname_webserver = response['Reservations'][0]['Instances'][0]['PublicIpAddress']
interface_webserver = response['Reservations'][0]['Instances'][0]['NetworkInterfaces'][0]['NetworkInterfaceId']

response = ec2.describe_instances(InstanceIds=[serveurbdd_instance_id])
hostname_dbserver = response['Reservations'][0]['Instances'][0]['PrivateIpAddress']
interface_dbserver = response['Reservations'][0]['Instances'][0]['NetworkInterfaces'][0]['NetworkInterfaceId']

response = ec2.describe_instances(InstanceIds=[serveurmir_instance_id])
hostname_mirserver = response['Reservations'][0]['Instances'][0]['PrivateIpAddress']
interface_mirserver = response['Reservations'][0]['Instances'][0]['NetworkInterfaces'][0]['NetworkInterfaceId']

info = {
    'hostname_webserver': hostname_webserver,
    'interface_webserver': interface_webserver,

    'hostname_dbserver': hostname_dbserver,
    'interface_dbserver': interface_dbserver,

    'hostname_mirserver': hostname_mirserver,
    'interface_mirserver': interface_mirserver
}
with open('instance_infos.json', 'w', encoding='utf-8') as file: file.write(json.dumps(info))


traffic_mirror_target = ec2.create_traffic_mirror_target(
    NetworkInterfaceId=interface_mirserver
)
traffic_mirror_target_id = traffic_mirror_target['TrafficMirrorTarget']['TrafficMirrorTargetId']
print(f'Create Traffic Mirror Target with ID {traffic_mirror_target_id}')

traffic_mirror_filter = ec2.create_traffic_mirror_filter()
traffic_mirror_filter_id = traffic_mirror_filter['TrafficMirrorFilter']['TrafficMirrorFilterId']
print(f'Create Traffic Mirror Filter with ID {traffic_mirror_filter_id}')

traffic_mirror_filter_rule = ec2.create_traffic_mirror_filter_rule(
    TrafficMirrorFilterId=traffic_mirror_filter_id,
    TrafficDirection='INGRESS',
    RuleNumber=1,
    RuleAction='accept',
    Protocol=6,
    DestinationPortRange={
        'FromPort': 80,
        'ToPort': 80
    },
    DestinationCidrBlock='0.0.0.0/0',
    SourceCidrBlock='0.0.0.0/0'
)
traffic_mirror_filter_rule_id = traffic_mirror_filter_rule['TrafficMirrorFilterRule']['TrafficMirrorFilterRuleId']
print(f'Create Traffic Mirror Filter Rule with ID {traffic_mirror_filter_rule_id}')

traffic_mirror_session = ec2.create_traffic_mirror_session(
    NetworkInterfaceId=interface_webserver,
    TrafficMirrorTargetId=traffic_mirror_target_id,
    TrafficMirrorFilterId=traffic_mirror_filter_id,
    SessionNumber=1
)
traffic_mirror_session_id = traffic_mirror_session['TrafficMirrorSession']['TrafficMirrorSessionId']
print(f'Create Traffic Mirror Session with ID {traffic_mirror_session_id}')