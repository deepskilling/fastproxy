# AWS EC2 Launch Configuration
# Copy this file to config.py and customize as needed

# Instance Configuration
INSTANCE_TYPE = 't3.xlarge'  # Options: t3.xlarge (4 vCPU, 16GB) or t3.2xlarge (8 vCPU, 32GB)
VOLUME_SIZE = 100  # GB
INSTANCE_NAME = 'FastProxy-Instance'

# Key Pair Configuration
KEY_NAME = 'fastproxy-key'

# Security Group Configuration
SECURITY_GROUP_NAME = 'fastproxy-sg'

# Additional ports to open (beyond SSH, HTTP, HTTPS, 8000)
ADDITIONAL_PORTS = [
    # {'port': 3000, 'description': 'React Dev Server'},
    # {'port': 8001, 'description': 'Backend API'},
]

# AMI Configuration (leave None to auto-detect latest Amazon Linux 2023)
AMI_ID = None

# AWS Region (leave None to use default from AWS CLI config)
REGION = None

