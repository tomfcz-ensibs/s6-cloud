import paramiko, json

def ssh_command(hostname, key_filename, commands):
    outputs = []

    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh_client.connect(hostname, port=22, username='ec2-user', key_filename=key_filename)

        for command in commands:
            stdin, stdout, stderr = ssh_client.exec_command(command)
            output = stdout.read().decode('utf-8')

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

with open('instance_infos.json', 'r', encoding='utf-8') as file:
    instance_infos = json.loads(file.read())

hostname_webserver = instance_infos['hostname_webserver']
hostname_dbserver = instance_infos['hostname_dbserver']
hostname_mirserver = instance_infos['hostname_mirserver']

key_path = './labsuser.pem'
with open(key_path, 'r', encoding='utf-8') as file: key_content = file.read()

# Starting configuration of web server
print('Starting configuration of web server')
webserver_script_path = 'https://raw.githubusercontent.com/tomfcz-ensibs/s6-cloud/main/tp3/sample_files/create_webser.sh'
webserver_keycopy = ssh_command(hostname_webserver, key_path, [
    f'echo "{key_content}" > ~/labsuser.pem',
    'chmod 600 ~/labsuser.pem'
])
webserver_install = ssh_command(hostname_webserver, key_path, [
    f'wget {webserver_script_path}',
    f'bash create_webser.sh {hostname_dbserver}'
])
print('Web server configuration completed')

# Starting configuration of database server
print('Starting configuration of database server')
dbserver_script_path = 'https://raw.githubusercontent.com/tomfcz-ensibs/s6-cloud/main/tp3/sample_files/create_dbserver.sh'
ssh_command_via_tunnel(
    hostname_webserver, 22, 'ec2-user', key_path,
    hostname_dbserver, 22, 'ec2-user', key_path,
    [
        f'wget {dbserver_script_path}',
        f'sudo bash create_dbserver.sh'
    ]
)
print('Database server configuration completed')

# Starting configuration of mirroring server
print('Starting configuration of mirroring server')
mirserver_script_path = 'https://raw.githubusercontent.com/tomfcz-ensibs/s6-cloud/main/tp3/sample_files/create_mirserver.sh'
ssh_command_via_tunnel(
    hostname_webserver, 22, 'ec2-user', key_path,
    hostname_mirserver, 22, 'ubuntu', key_path,
    [
        f'wget {mirserver_script_path}',
        f'sudo bash create_mirserver.sh'
    ]
)
print('Mirroring server configuration completed')