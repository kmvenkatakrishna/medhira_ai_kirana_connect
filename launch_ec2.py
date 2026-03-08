"""
Launch EC2 instance for KiranaConnect backend.
Automatically configures security group, launches instance with user-data script.
"""
import boto3
import time
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from backend.config import AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY

ec2 = boto3.client(
    "ec2", region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)
ec2_resource = boto3.resource(
    "ec2", region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

# User-data script — runs on first boot
USER_DATA = f"""#!/bin/bash
set -e
exec > /var/log/kirana-setup.log 2>&1

echo "=== KiranaConnect Setup Starting ==="

# Install dependencies
apt-get update -y
apt-get install -y python3 python3-pip python3-venv git nginx

# Clone repo
cd /home/ubuntu
git clone -b dev-adarsh https://github.com/kmvenkatakrishna/medhira_ai_kirana_connect.git app
cd app

# Create venv and install
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt

# Create .env file with credentials
cat > .env << 'ENVEOF'
AWS_REGION={AWS_REGION}
AWS_ACCESS_KEY_ID={AWS_ACCESS_KEY_ID}
AWS_SECRET_ACCESS_KEY={AWS_SECRET_ACCESS_KEY}
USE_LOCAL_DATA=true
DEBUG=false
BEDROCK_ENABLED=true
S3_BUCKET=kirana-connect-media
ENVEOF

# Setup systemd service
cat > /etc/systemd/system/kiranaconnect.service << 'SVCEOF'
[Unit]
Description=KiranaConnect AI Backend
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/app
Environment=PATH=/home/ubuntu/app/venv/bin:/usr/bin
ExecStart=/home/ubuntu/app/venv/bin/python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
SVCEOF

# Setup Nginx
cat > /etc/nginx/sites-available/kiranaconnect << 'NGXEOF'
server {{
    listen 80;
    server_name _;

    # CORS headers for S3 frontend
    add_header 'Access-Control-Allow-Origin' '*' always;
    add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
    add_header 'Access-Control-Allow-Headers' 'Content-Type, Authorization' always;

    location / {{
        if ($request_method = 'OPTIONS') {{
            return 204;
        }}
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 300s;
    }}
}}
NGXEOF

ln -sf /etc/nginx/sites-available/kiranaconnect /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl restart nginx

# Start the service
chown -R ubuntu:ubuntu /home/ubuntu/app
systemctl daemon-reload
systemctl enable kiranaconnect
systemctl start kiranaconnect

echo "=== KiranaConnect Setup Complete ==="
"""


def create_security_group():
    """Create security group allowing HTTP and SSH."""
    sg_name = "kiranaconnect-sg"
    try:
        existing = ec2.describe_security_groups(
            Filters=[{"Name": "group-name", "Values": [sg_name]}]
        )
        if existing["SecurityGroups"]:
            sg_id = existing["SecurityGroups"][0]["GroupId"]
            print(f"  [SKIP] Security group exists: {sg_id}")
            return sg_id
    except Exception:
        pass

    try:
        # Get default VPC
        vpcs = ec2.describe_vpcs(Filters=[{"Name": "isDefault", "Values": ["true"]}])
        vpc_id = vpcs["Vpcs"][0]["VpcId"]

        sg = ec2.create_security_group(
            GroupName=sg_name,
            Description="KiranaConnect API Server",
            VpcId=vpc_id
        )
        sg_id = sg["GroupId"]

        # Allow SSH (22), HTTP (80), and app port (8000)
        ec2.authorize_security_group_ingress(
            GroupId=sg_id,
            IpPermissions=[
                {"IpProtocol": "tcp", "FromPort": 22, "ToPort": 22,
                 "IpRanges": [{"CidrIp": "0.0.0.0/0"}]},
                {"IpProtocol": "tcp", "FromPort": 80, "ToPort": 80,
                 "IpRanges": [{"CidrIp": "0.0.0.0/0"}]},
                {"IpProtocol": "tcp", "FromPort": 8000, "ToPort": 8000,
                 "IpRanges": [{"CidrIp": "0.0.0.0/0"}]},
            ]
        )
        print(f"  [OK] Created security group: {sg_id}")
        return sg_id
    except Exception as e:
        print(f"  [ERR] {e}")
        return None


def get_ubuntu_ami():
    """Get latest Ubuntu 24.04 AMI for the region."""
    images = ec2.describe_images(
        Filters=[
            {"Name": "name", "Values": ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]},
            {"Name": "state", "Values": ["available"]},
        ],
        Owners=["099720109477"]  # Canonical
    )
    if not images["Images"]:
        # Fallback to 22.04
        images = ec2.describe_images(
            Filters=[
                {"Name": "name", "Values": ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]},
                {"Name": "state", "Values": ["available"]},
            ],
            Owners=["099720109477"]
        )
    sorted_images = sorted(images["Images"], key=lambda x: x["CreationDate"], reverse=True)
    ami_id = sorted_images[0]["ImageId"]
    print(f"  [OK] AMI: {ami_id} ({sorted_images[0]['Name'][:60]}...)")
    return ami_id


def launch_instance(sg_id, ami_id):
    """Launch a t2.micro EC2 instance."""
    instances = ec2_resource.create_instances(
        ImageId=ami_id,
        InstanceType="t2.micro",
        MinCount=1, MaxCount=1,
        SecurityGroupIds=[sg_id],
        UserData=USER_DATA,
        TagSpecifications=[{
            "ResourceType": "instance",
            "Tags": [{"Key": "Name", "Value": "KiranaConnect-Server"}]
        }]
    )
    instance = instances[0]
    print(f"  [OK] Instance launched: {instance.id}")

    print("  Waiting for instance to start...")
    instance.wait_until_running()
    instance.reload()
    public_ip = instance.public_ip_address
    print(f"  [OK] Public IP: {public_ip}")
    return instance.id, public_ip


if __name__ == "__main__":
    print("=" * 50)
    print("  Launching KiranaConnect EC2 Server")
    print("=" * 50)

    print("\n[1/3] Security Group...")
    sg_id = create_security_group()

    print("\n[2/3] Finding Ubuntu AMI...")
    ami_id = get_ubuntu_ami()

    print("\n[3/3] Launching Instance...")
    instance_id, public_ip = launch_instance(sg_id, ami_id)

    print("\n" + "=" * 50)
    print(f"  EC2 Instance: {instance_id}")
    print(f"  Public IP:    {public_ip}")
    print(f"  Backend URL:  http://{public_ip}")
    print(f"  API Health:   http://{public_ip}/api/v1/health")
    print(f"  Frontend:     http://kirana-connect-media.s3-website.{AWS_REGION}.amazonaws.com/")
    print("=" * 50)
    print(f"\nNote: Server needs ~3-4 min to install deps and start.")
    print(f"Check: curl http://{public_ip}/api/v1/health")
