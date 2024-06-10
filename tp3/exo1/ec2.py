import boto3, time, paramiko, json

with open("vpc_infos.json",'r', encoding='utf-8') as file:
    infos = json.loads(file.read())

VPC_ID = infos['vpc_id']
SUBNET_PUB_ID = infos['subnet_pub_id']
SUBNET_PRI_ID = infos['subnet_priv_id']
SECURITY_PUB_ID = infos['security_group_pub_id']
SECURITY_PRI_ID = infos['security_group_priv_id']

def create_ec2_instance(ec2, security_group_id, subnet_id, AssociatePublicIpAddress = False):
    response = ec2.run_instances(
        ImageId='ami-00beae93a2d981137',
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

def ssh_command(hostname, key_filename, commands):
    outputs = []

    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh_client.connect(hostname, port=22, username='ec2-user', key_filename=key_filename)

        for command in commands:
            stdin, stdout, stderr = ssh_client.exec_command(command)
            output = stdout.read().decode('utf-8')

            print(output)

            outputs.append(output)
    except paramiko.AuthenticationException:
        print('Authentication failed, please verify your credentials.')
    except paramiko.SSHException as ssh_err:
        print(f'Unable to establish SSH connection: {ssh_err}')
    finally:
        ssh_client.close()

    return outputs

def ssh_command_via_tunnel(
        jump_host, jump_port, jump_user, jump_keyfile_path,
        target_host, target_port, target_user, target_keyfile_path,
        commands
    ):
    outputs = []

    try:
        # Connect to the jump host
        jump_client = paramiko.SSHClient()
        jump_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        jump_client.connect(jump_host, port=jump_port, username=jump_user, key_filename=jump_keyfile_path)

        # Open a transport session to the jump host
        jump_transport = jump_client.get_transport()

        # Open a channel to the target host through the jump host
        dest_addr = (target_host, target_port)
        local_addr = ('localhost', 0)
        jump_channel = jump_transport.open_channel("direct-tcpip", dest_addr, local_addr)

        # Connect to the target host via the jump channel
        target_client = paramiko.SSHClient()
        target_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        target_client.connect(target_host, port=target_port, username=target_user, key_filename=target_keyfile_path, sock=jump_channel)

        # Execute the command on the target host
        for command in commands:
            stdin, stdout, stderr = target_client.exec_command(command)

            # Read the command output
            output = stdout.read().decode('utf-8')

            outputs.append(output)

        # Close the connections
        target_client.close()
        jump_client.close()

        return outputs

    except Exception as e:
        return [f"Exception: {str(e)}"]

##########
"""
ec2 = boto3.client('ec2', region_name='us-east-1')
 
serveurweb_instance = create_ec2_instance(ec2, SECURITY_PUB_ID, SUBNET_PUB_ID, True)
serveurweb_instance_id = serveurweb_instance['InstanceId']

serveurbdd_instance = create_ec2_instance(ec2, SECURITY_PRI_ID, SUBNET_PRI_ID, False)
serveurbdd_instance_id = serveurbdd_instance['InstanceId']

wait_for_instance_state(ec2, serveurweb_instance_id)
wait_for_instance_state(ec2, serveurbdd_instance_id)

response = ec2.describe_instances(InstanceIds=[serveurweb_instance_id])
hostname_webserver = response['Reservations'][0]['Instances'][0]['PublicIpAddress']

response = ec2.describe_instances(InstanceIds=[serveurbdd_instance_id])
hostname_dbserver = response['Reservations'][0]['Instances'][0]['PrivateIpAddress']

info = {
    'hostname_webserver': hostname_webserver,
    'hostname_dbserver' : hostname_dbserver
}
with open('instance_infos.json', 'w', encoding='utf-8') as file: file.write(json.dumps(info))
print(info)

print('Waiting for ssh service to launch (10s)')
time.sleep(10)
"""

with open('instance_infos.json', 'r', encoding='utf-8') as file:
    instance_infos = json.loads(file.read())

hostname_webserver = instance_infos['hostname_webserver']
hostname_dbserver = instance_infos['hostname_dbserver']

key_path = './labsuser.pem'
with open(key_path, 'r', encoding='utf-8') as file: key_content = file.read()


# Starting configuration of web server
webserver_script_path = 'https://raw.githubusercontent.com/tomfcz-ensibs/s6-cloud/main/tp3/exo1/create_webser.sh'
webserver_keycopy = ssh_command(hostname_webserver, key_path, [
    f'echo "{key_content}" > ~/labsuser.pem',
    'chmod 600 ~/labsuser.pem'
])
webserver_install = ssh_command(hostname_webserver, key_path, [
    f'wget {webserver_script_path}',
    f'bash create_webser.sh {hostname_dbserver}'
])


# Starting configuration of database server
dbserver_script_path = 'https://raw.githubusercontent.com/tomfcz-ensibs/s6-cloud/main/tp3/exo1/create_dbserver.sh'
ssh_command_via_tunnel(
    hostname_webserver, 22, 'ec2-user', key_path,
    hostname_dbserver, 22, 'ec2-user', key_path,
    [
        f'wget {dbserver_script_path}',
        f'bash create_dbserver.sh {hostname_dbserver}'
    ]
)