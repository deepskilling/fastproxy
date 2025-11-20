# AWS EC2 Launch Script

This script automatically launches an EC2 instance with the following specifications:
- **RAM**: 16 GB (t3.xlarge) or 32 GB (t3.2xlarge)
- **CPU**: 4 vCPUs (t3.xlarge) or 8 vCPUs (t3.2xlarge)
- **Storage**: 100 GB SSD (gp3)
- **OS**: Amazon Linux 2023 (latest)
- **Key Pair**: Automatically creates and downloads

## Prerequisites

1. **AWS CLI configured** with default profile:
   ```bash
   aws configure
   ```
   Provide your:
   - AWS Access Key ID
   - AWS Secret Access Key
   - Default region (e.g., us-east-1)
   - Default output format (json)

2. **Python 3.7+** installed

3. **boto3** installed:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

```bash
python launch_ec2.py
```

The script will:
1. ✅ Auto-detect the latest Amazon Linux 2023 AMI
2. ✅ Create a key pair and save as `fastproxy-key.pem`
3. ✅ Create a security group with SSH (22), HTTP (80), HTTPS (443), and port 8000 access
4. ✅ Launch the EC2 instance
5. ✅ Display connection information

### Configuration Options

Edit the `CONFIG` dictionary in `launch_ec2.py` to customize:

```python
CONFIG = {
    'instance_type': 't3.xlarge',      # Change to 't3.2xlarge' for 8 vCPUs
    'volume_size': 100,                # GB
    'key_name': 'fastproxy-key',
    'security_group_name': 'fastproxy-sg',
    'instance_name': 'FastProxy-Instance',
}
```

### Instance Type Options

| Instance Type | vCPUs | RAM   | Cost/Hour (approx) |
|--------------|-------|-------|-------------------|
| t3.xlarge    | 4     | 16 GB | $0.1664          |
| t3.2xlarge   | 8     | 32 GB | $0.3328          |
| t3a.xlarge   | 4     | 16 GB | $0.1504 (AMD)    |
| t3a.2xlarge  | 8     | 32 GB | $0.3008 (AMD)    |

## After Launch

### Connect to Instance

```bash
ssh -i fastproxy-key.pem ec2-user@<PUBLIC_IP>
```

### Install FastProxy on Instance

```bash
# Update system
sudo dnf update -y

# Install Python and Git
sudo dnf install -y python3 python3-pip git

# Clone FastProxy
git clone <your-repo-url>
cd fastproxy

# Install dependencies
pip3 install -r requirements.txt

# Run FastProxy
python3 main.py
```

## Security Group Ports

The script automatically opens these ports:
- **22**: SSH
- **80**: HTTP
- **443**: HTTPS
- **8000**: FastProxy default port

## Files Created

- `fastproxy-key.pem` - Private key file (chmod 400)
- Key pair in AWS with name: `fastproxy-key`
- Security group: `fastproxy-sg`

## Cleanup

To terminate the instance and clean up:

```bash
# Terminate instance
aws ec2 terminate-instances --instance-ids <instance-id>

# Delete security group (after instance is terminated)
aws ec2 delete-security-group --group-name fastproxy-sg

# Delete key pair
aws ec2 delete-key-pair --key-name fastproxy-key
rm fastproxy-key.pem
```

## Cost Estimation

Based on t3.xlarge in us-east-1:
- **Compute**: ~$0.17/hour = ~$122/month (if running 24/7)
- **Storage**: 100 GB gp3 = ~$8/month
- **Total**: ~$130/month

💡 **Tip**: Stop the instance when not in use to save on compute costs!

## Troubleshooting

### AWS CLI not configured
```bash
aws configure
```

### boto3 not installed
```bash
pip install boto3
```

### Permission denied for key file
```bash
chmod 400 fastproxy-key.pem
```

### Cannot connect via SSH
- Check security group rules
- Verify instance is in "running" state
- Ensure you're using the correct public IP
- Check your local firewall settings

## Support

For issues or questions, refer to:
- AWS EC2 Documentation: https://docs.aws.amazon.com/ec2/
- boto3 Documentation: https://boto3.amazonaws.com/v1/documentation/api/latest/index.html

