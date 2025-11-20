#!/usr/bin/env python3
"""
AWS EC2 Instance Launch Script
Creates an EC2 instance with specified configuration:
- 8GB+ RAM
- 4 or 8 CPU cores
- 100GB HDD
- Auto-creates and downloads key pair
"""

import boto3
import os
import sys
import argparse
from datetime import datetime
from botocore.exceptions import ClientError

# Configuration
CONFIG = {
    'instance_type': 't3.xlarge',  # 4 vCPUs, 16 GB RAM (change to t3.2xlarge for 8 vCPUs, 32 GB)
    'volume_size': 100,  # GB
    'key_name': 'fastproxy-key',
    'security_group_name': 'fastproxy-sg',
    'instance_name': 'FastProxy-Instance',
    'ami_id': None,  # Will auto-detect latest Amazon Linux 2023 AMI
    'region': None,  # Will use default region from AWS config
    'vpc_id': 'vpc-027a4e812349b535d',  # VPC with internet gateway
    'subnet_id': 'subnet-076eb0dd6151966ff',  # Public subnet with auto-assign public IP
}


def get_latest_amazon_linux_ami(ec2_client):
    """Get the latest Amazon Linux 2023 AMI ID"""
    try:
        response = ec2_client.describe_images(
            Owners=['amazon'],
            Filters=[
                {'Name': 'name', 'Values': ['al2023-ami-2023.*-x86_64']},
                {'Name': 'state', 'Values': ['available']},
                {'Name': 'architecture', 'Values': ['x86_64']},
            ],
        )
        
        # Sort by creation date and get the latest
        images = sorted(response['Images'], key=lambda x: x['CreationDate'], reverse=True)
        if images:
            ami_id = images[0]['ImageId']
            print(f"✅ Using latest Amazon Linux 2023 AMI: {ami_id}")
            return ami_id
        else:
            print("❌ No Amazon Linux 2023 AMI found")
            return None
    except ClientError as e:
        print(f"❌ Error finding AMI: {e}")
        return None


def create_key_pair(ec2_client, key_name, auto_confirm=False):
    """Create EC2 key pair and save to file"""
    try:
        # Check if key pair already exists
        try:
            ec2_client.describe_key_pairs(KeyNames=[key_name])
            print(f"⚠️  Key pair '{key_name}' already exists")
            if auto_confirm:
                print(f"ℹ️  Using existing key pair (auto-confirm enabled)")
                return None
            try:
                response = input(f"Do you want to delete and recreate it? (yes/no): ")
                if response.lower() == 'yes':
                    ec2_client.delete_key_pair(KeyName=key_name)
                    print(f"🗑️  Deleted existing key pair: {key_name}")
                else:
                    print(f"ℹ️  Using existing key pair: {key_name}")
                    return None
            except EOFError:
                print(f"ℹ️  Using existing key pair (cannot read input)")
                return None
        except ClientError:
            pass  # Key doesn't exist, create it
        
        # Create new key pair
        response = ec2_client.create_key_pair(KeyName=key_name)
        private_key = response['KeyMaterial']
        
        # Save private key to file
        key_file = f"{key_name}.pem"
        with open(key_file, 'w') as f:
            f.write(private_key)
        
        # Set proper permissions (read-only for owner)
        os.chmod(key_file, 0o400)
        
        print(f"✅ Key pair created and saved to: {os.path.abspath(key_file)}")
        print(f"   Use this command to SSH: ssh -i {key_file} ec2-user@<instance-ip>")
        return key_file
        
    except ClientError as e:
        print(f"❌ Error creating key pair: {e}")
        return None


def create_security_group(ec2_client, group_name, vpc_id=None):
    """Create security group with SSH, HTTP, and HTTPS access"""
    try:
        # Check if security group already exists in the specified VPC
        try:
            filters = [{'Name': 'group-name', 'Values': [group_name]}]
            if vpc_id:
                filters.append({'Name': 'vpc-id', 'Values': [vpc_id]})
            
            response = ec2_client.describe_security_groups(Filters=filters)
            if response['SecurityGroups']:
                sg_id = response['SecurityGroups'][0]['GroupId']
                vpc_id = response['SecurityGroups'][0]['VpcId']
                print(f"ℹ️  Using existing security group: {sg_id} in VPC: {vpc_id}")
                return sg_id, vpc_id
        except ClientError:
            pass  # Security group doesn't exist, create it
        
        # Use specified VPC or get any available VPC
        if not vpc_id:
            ec2_resource = boto3.resource('ec2')
            
            # Try to get default VPC
            vpcs = list(ec2_resource.vpcs.filter(Filters=[{'Name': 'isDefault', 'Values': ['true']}]))
            
            if not vpcs:
                # No default VPC, get any available VPC
                print("ℹ️  No default VPC found, using first available VPC...")
                vpcs = list(ec2_resource.vpcs.all())
                
                if not vpcs:
                    print("❌ No VPCs found in this region")
                    return None, None
            
            vpc_id = vpcs[0].id
        
        print(f"ℹ️  Using VPC: {vpc_id}")
        
        # Create security group
        response = ec2_client.create_security_group(
            GroupName=group_name,
            Description='Security group for FastProxy EC2 instance',
            VpcId=vpc_id
        )
        sg_id = response['GroupId']
        
        # Add inbound rules
        ec2_client.authorize_security_group_ingress(
            GroupId=sg_id,
            IpPermissions=[
                # SSH access
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 22,
                    'ToPort': 22,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0', 'Description': 'SSH access'}]
                },
                # HTTP access
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 80,
                    'ToPort': 80,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0', 'Description': 'HTTP access'}]
                },
                # HTTPS access
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 443,
                    'ToPort': 443,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0', 'Description': 'HTTPS access'}]
                },
                # FastProxy port
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 8000,
                    'ToPort': 8000,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0', 'Description': 'FastProxy port'}]
                },
            ]
        )
        
        print(f"✅ Security group created: {sg_id}")
        return sg_id, vpc_id
        
    except ClientError as e:
        # Check if it's a duplicate error
        if 'InvalidGroup.Duplicate' in str(e):
            # Security group already exists, get it
            try:
                response = ec2_client.describe_security_groups(
                    Filters=[
                        {'Name': 'group-name', 'Values': [group_name]},
                        {'Name': 'vpc-id', 'Values': [vpc_id]}
                    ]
                )
                if response['SecurityGroups']:
                    sg_id = response['SecurityGroups'][0]['GroupId']
                    print(f"ℹ️  Using existing security group: {sg_id}")
                    return sg_id, vpc_id
            except Exception as lookup_error:
                print(f"❌ Error looking up security group: {lookup_error}")
        
        print(f"❌ Error creating security group: {e}")
        return None, None


def get_subnet_from_vpc(ec2_client, vpc_id):
    """Get a subnet from the specified VPC"""
    try:
        response = ec2_client.describe_subnets(
            Filters=[
                {'Name': 'vpc-id', 'Values': [vpc_id]},
                {'Name': 'state', 'Values': ['available']}
            ]
        )
        
        if response['Subnets']:
            subnet_id = response['Subnets'][0]['SubnetId']
            print(f"ℹ️  Using Subnet: {subnet_id}")
            return subnet_id
        else:
            print("❌ No available subnets found in VPC")
            return None
    except ClientError as e:
        print(f"❌ Error finding subnet: {e}")
        return None


def launch_instance(ec2_client, ami_id, instance_type, key_name, security_group_id, subnet_id, volume_size, instance_name):
    """Launch EC2 instance with specified configuration"""
    try:
        # Launch instance
        launch_params = {
            'ImageId': ami_id,
            'InstanceType': instance_type,
            'KeyName': key_name,
            'SecurityGroupIds': [security_group_id],
            'MinCount': 1,
            'MaxCount': 1,
            'BlockDeviceMappings': [
                {
                    'DeviceName': '/dev/xvda',  # Root device for Amazon Linux
                    'Ebs': {
                        'VolumeSize': volume_size,
                        'VolumeType': 'gp3',  # General Purpose SSD (gp3)
                        'DeleteOnTermination': True,
                        'Encrypted': True,  # Enable encryption at rest
                    }
                }
            ],
            'TagSpecifications': [
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {'Key': 'Name', 'Value': instance_name},
                        {'Key': 'CreatedBy', 'Value': 'FastProxy-Launch-Script'},
                        {'Key': 'CreatedAt', 'Value': datetime.now().isoformat()},
                    ]
                }
            ],
            'MetadataOptions': {
                'HttpTokens': 'required',  # Enforce IMDSv2
                'HttpPutResponseHopLimit': 1,
            }
        }
        
        # Add subnet if provided
        if subnet_id:
            launch_params['SubnetId'] = subnet_id
        
        response = ec2_client.run_instances(**launch_params)
        
        instance_id = response['Instances'][0]['InstanceId']
        print(f"✅ EC2 instance launched: {instance_id}")
        print(f"   Instance Type: {instance_type}")
        print(f"   Storage: {volume_size} GB (Encrypted)")
        
        # Wait for instance to be running
        print(f"⏳ Waiting for instance to start...")
        waiter = ec2_client.get_waiter('instance_running')
        waiter.wait(InstanceIds=[instance_id])
        
        # Get instance details
        response = ec2_client.describe_instances(InstanceIds=[instance_id])
        instance = response['Reservations'][0]['Instances'][0]
        
        public_ip = instance.get('PublicIpAddress', 'N/A')
        private_ip = instance.get('PrivateIpAddress', 'N/A')
        
        print(f"\n{'='*60}")
        print(f"🎉 EC2 INSTANCE SUCCESSFULLY LAUNCHED!")
        print(f"{'='*60}")
        print(f"Instance ID:     {instance_id}")
        print(f"Instance Type:   {instance_type}")
        print(f"Public IP:       {public_ip}")
        print(f"Private IP:      {private_ip}")
        print(f"Key Name:        {key_name}")
        print(f"Storage:         {volume_size} GB")
        print(f"State:           {instance['State']['Name']}")
        print(f"{'='*60}")
        
        if public_ip != 'N/A':
            print(f"\n📝 SSH Connection Command:")
            print(f"   ssh -i {key_name}.pem ec2-user@{public_ip}")
        
        return instance_id
        
    except ClientError as e:
        print(f"❌ Error launching instance: {e}")
        return None


def main():
    """Main function"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Launch AWS EC2 instance')
    parser.add_argument('-y', '--yes', action='store_true', help='Skip confirmation prompt')
    parser.add_argument('--type', default=CONFIG['instance_type'], help='Instance type (default: t3.xlarge)')
    parser.add_argument('--size', type=int, default=CONFIG['volume_size'], help='Storage size in GB (default: 100)')
    args = parser.parse_args()
    
    # Update config from command line
    CONFIG['instance_type'] = args.type
    CONFIG['volume_size'] = args.size
    
    print("\n" + "="*60)
    print("  AWS EC2 Instance Launch Script")
    print("="*60 + "\n")
    
    # Initialize AWS clients
    try:
        session = boto3.Session(profile_name='default')
        ec2_client = session.client('ec2')
        region = session.region_name or 'us-east-1'
        print(f"🌍 Using AWS Region: {region}")
    except Exception as e:
        print(f"❌ Error initializing AWS session: {e}")
        print("   Make sure AWS CLI is configured with 'aws configure'")
        sys.exit(1)
    
    # Display configuration
    print(f"\n📋 Instance Configuration:")
    print(f"   Instance Type: {CONFIG['instance_type']}")
    print(f"   Storage:       {CONFIG['volume_size']} GB (Encrypted)")
    print(f"   Key Name:      {CONFIG['key_name']}")
    print(f"   Instance Name: {CONFIG['instance_name']}\n")
    
    # Confirm before proceeding
    if not args.yes:
        try:
            response = input("Do you want to proceed? (yes/no): ")
            if response.lower() != 'yes':
                print("❌ Launch cancelled")
                sys.exit(0)
        except EOFError:
            print("❌ Cannot read input. Use --yes flag to skip confirmation.")
            sys.exit(1)
    else:
        print("✅ Auto-confirming launch (--yes flag provided)\n")
    
    print("")
    
    # Step 1: Get AMI ID
    ami_id = CONFIG['ami_id']
    if not ami_id:
        ami_id = get_latest_amazon_linux_ami(ec2_client)
        if not ami_id:
            sys.exit(1)
    
    # Step 2: Create key pair
    key_file = create_key_pair(ec2_client, CONFIG['key_name'], auto_confirm=args.yes)
    
    # Step 3: Create security group
    result = create_security_group(ec2_client, CONFIG['security_group_name'], vpc_id=CONFIG.get('vpc_id'))
    if not result or result == (None, None):
        sys.exit(1)
    sg_id, vpc_id = result
    
    # Step 3.5: Get subnet from config or VPC
    subnet_id = CONFIG.get('subnet_id')
    if not subnet_id:
        subnet_id = get_subnet_from_vpc(ec2_client, vpc_id)
        if not subnet_id:
            print("⚠️  No subnet found, will try without subnet specification")
            subnet_id = None
    else:
        print(f"ℹ️  Using configured subnet: {subnet_id}")
    
    # Step 4: Launch instance
    instance_id = launch_instance(
        ec2_client,
        ami_id,
        CONFIG['instance_type'],
        CONFIG['key_name'],
        sg_id,
        subnet_id,
        CONFIG['volume_size'],
        CONFIG['instance_name']
    )
    
    if instance_id:
        print(f"\n✅ Instance launch completed successfully!")
        print(f"\n💡 Next steps:")
        print(f"   1. Wait a few minutes for the instance to fully initialize")
        print(f"   2. Use the SSH command above to connect")
        print(f"   3. View instance in AWS Console: https://console.aws.amazon.com/ec2/")
    else:
        print("\n❌ Instance launch failed")
        sys.exit(1)


if __name__ == '__main__':
    main()

