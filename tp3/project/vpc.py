import boto3, time, json

def wait_for_nat(ec2,nat_gateway_id):
    attempts = 0
    max_attempts = 1000
    interval = 30
    while attempts < max_attempts:
        response = ec2.describe_nat_gateways(NatGatewayIds=[nat_gateway_id])
        nat_gateway = response['NatGateways'][0]
        state = nat_gateway['State']
        print(f"NAT Gateway state: {state}")
        if state == 'available':
            print("NAT Gateway is now available.")
            return
        elif state == 'failed':
            raise Exception("NAT Gateway creation failed.")
        time.sleep(interval)
        attempts += 1
    raise Exception("Timed out waiting for NAT Gateway to become available.")

ec2 = boto3.client('ec2',region_name='us-east-1')
vpc = ec2.create_vpc(
        CidrBlock='10.0.0.0/16'
)
vpc_id = vpc['Vpc']['VpcId']
print(f'Created VPC with ID: {vpc_id}')


subnet_pub = ec2.create_subnet(CidrBlock='10.0.0.0/24',VpcId=vpc_id)
subnet_pub_id = subnet_pub['Subnet']['SubnetId']
print(f"Subnet created with ID {subnet_pub_id}")

subnet_priv = ec2.create_subnet(CidrBlock='10.0.1.0/24',VpcId=vpc_id)
subnet_priv_id = subnet_priv['Subnet']['SubnetId']
print(f"Subnet created with ID {subnet_priv_id}")


int_gateway = ec2.create_internet_gateway()
int_gateway_id = int_gateway['InternetGateway']['InternetGatewayId']
response = ec2.attach_internet_gateway(
    InternetGatewayId=int_gateway_id,
    VpcId=vpc_id
)
print(f"Internet Gateway created with ID {int_gateway_id}")


route_table_pub = ec2.create_route_table(VpcId=vpc_id)
route_table_pub_id = route_table_pub['RouteTable']['RouteTableId']
print(f"Route Table created with ID {route_table_pub_id}")

route_table_priv = ec2.create_route_table(VpcId=vpc_id)
route_table_priv_id = route_table_priv['RouteTable']['RouteTableId']
print(f"Route Table created with ID {route_table_priv_id}")

response = ec2.associate_route_table(
    RouteTableId=route_table_pub_id,
    SubnetId=subnet_pub_id,
)
print(f"Route Table {route_table_pub_id} Associated to Subnet {subnet_pub_id}")

response = ec2.associate_route_table(
    RouteTableId=route_table_priv_id,
    SubnetId=subnet_priv_id,
)
print(f"Route Table {route_table_priv_id} Associated to Subnet {subnet_priv_id}")


allocation = ec2.allocate_address(Domain='vpc')
allocation_id = allocation['AllocationId']
allocation_ip = allocation['PublicIp']
print(f"Created Elastic IP {allocation_ip} With ID {allocation_id}")

nat_gateway = ec2.create_nat_gateway(SubnetId=subnet_pub_id,ConnectivityType="public",AllocationId=allocation_id)
nat_gateway_id = nat_gateway['NatGateway']['NatGatewayId']
print(f"Create NAT Gateway with ID {nat_gateway_id}")
print("Waiting for NAT Gateway to be ready")
wait_for_nat(ec2,nat_gateway_id)


response = ec2.create_route(DestinationCidrBlock='0.0.0.0/0',GatewayId=int_gateway_id,RouteTableId=route_table_pub_id)
print(f"Edited route table {route_table_pub_id}")

response = ec2.create_route(DestinationCidrBlock='0.0.0.0/0',GatewayId=nat_gateway_id,RouteTableId=route_table_priv_id)
print(f"Edited route table {route_table_priv_id}")


security_group_pub = ec2.create_security_group(Description="SG_PUB",GroupName="SG_PUB",VpcId=vpc_id)
security_group_pub_id = security_group_pub['GroupId']
print(f"Created Security Group with ID {security_group_pub_id}")

security_group_priv = ec2.create_security_group(Description="SG_PRIV",GroupName="SG_PRIV",VpcId=vpc_id)
security_group_priv_id = security_group_priv['GroupId']
print(f"Created Security Group with ID {security_group_priv_id}")

response = ec2.authorize_security_group_ingress(
    GroupId=security_group_priv_id,
    IpPermissions=[
        {
            'FromPort': 1,
            'IpProtocol': '-1',
            'IpRanges': [
                {
                    'CidrIp': '0.0.0.0/0',
                    'Description': 'Full Access',
                },
            ],
            'ToPort': 65535,
        },
    ],
)
print(f"Create Full Access Policies for Security Group with ID {security_group_priv_id}")

response = ec2.authorize_security_group_ingress(
    GroupId=security_group_pub_id,
    IpPermissions=[
        {
            'FromPort': 1,
            'IpProtocol': '-1',
            'IpRanges': [
                {
                    'CidrIp': '0.0.0.0/0',
                    'Description': 'Full Access',
                },
            ],
            'ToPort': 65535,
        },
    ],
)
print(f"Create Full Access Policies for Security Group with ID {security_group_pub_id}")


info = {
    'subnet_pub_id': subnet_pub_id,
    'subnet_priv_id' : subnet_priv_id,    
    'security_group_pub_id' : security_group_pub_id,
    'security_group_priv_id' : security_group_priv_id,
    'vpc_id' : vpc_id
}
with open('vpc_infos.json', 'w', encoding='utf-8') as file: file.write(json.dumps(info))