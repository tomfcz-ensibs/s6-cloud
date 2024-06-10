import boto3, time, json

with open('vpc_infos.json', 'r', encoding='utf-8') as file:
    infos = json.loads(file.read())

VPC_ID = infos['vpc_id']
SUBNET_PUB_ID = infos['subnet_pub_id']
SUBNET_PRI_ID = infos['subnet_priv_id']
SECURITY_PUB_ID = infos['security_group_pub_id']
SECURITY_PRI_ID = infos['security_group_priv_id']

def create_ec2_instance(ec2, image_id, security_group_id, subnet_id, AssociatePublicIpAddress = False):
    response = ec2.run_instances(
        ImageId=image_id,
        InstanceType='t2.micro',
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
 
serveurweb_instance = create_ec2_instance(ec2, 'ami-00beae93a2d981137', SECURITY_PUB_ID, SUBNET_PUB_ID, True)
serveurweb_instance_id = serveurweb_instance['InstanceId']

serveurbdd_instance = create_ec2_instance(ec2, 'ami-00beae93a2d981137', SECURITY_PRI_ID, SUBNET_PRI_ID, False)
serveurbdd_instance_id = serveurbdd_instance['InstanceId']

serveurmir_instance = create_ec2_instance(ec2, 'ami-04b70fa74e45c3917', SECURITY_PRI_ID, SUBNET_PRI_ID, False)
serveurmir_instance_id = serveurmir_instance['InstanceId']

wait_for_instance_state(ec2, serveurweb_instance_id)
wait_for_instance_state(ec2, serveurbdd_instance_id)
wait_for_instance_state(ec2, serveurmir_instance_id)

response = ec2.describe_instances(InstanceIds=[serveurweb_instance_id])
hostname_webserver = response['Reservations'][0]['Instances'][0]['PublicIpAddress']

response = ec2.describe_instances(InstanceIds=[serveurbdd_instance_id])
hostname_dbserver = response['Reservations'][0]['Instances'][0]['PrivateIpAddress']

response = ec2.describe_instances(InstanceIds=[serveurmir_instance_id])
hostname_mirserver = response['Reservations'][0]['Instances'][0]['PrivateIpAddress']

info = {
    'hostname_webserver': hostname_webserver,
    'hostname_dbserver': hostname_dbserver,
    'hostname_mirserver': hostname_mirserver
}
with open('instance_infos.json', 'w', encoding='utf-8') as file: file.write(json.dumps(info))
print(info)