"""
Create CloudFront distribution for HTTPS.
"""
import boto3
import time
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from backend.config import AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY

cf = boto3.client('cloudfront',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

EC2_ORIGIN = "ec2-3-109-201-10.ap-south-1.compute.amazonaws.com"

# Check if distribution already exists
print("Checking existing distributions...")
try:
    dists = cf.list_distributions()
    items = dists.get('DistributionList', {}).get('Items', [])
    if items:
        for d in items:
            origins = d.get('Origins', {}).get('Items', [])
            for o in origins:
                if EC2_ORIGIN in o.get('DomainName', ''):
                    domain = d["DomainName"]
                    status = d["Status"]
                    dist_id = d["Id"]
                    print(f"Distribution already exists: {domain}")
                    print(f"Status: {status}")
                    print(f"ID: {dist_id}")
                    print(f"HTTPS URL: https://{domain}")
                    sys.exit(0)
    print("No existing distribution found. Creating new one...")
except Exception as e:
    print(f"Error checking: {e}")

# Create CloudFront distribution
caller_ref = f"kiranaconnect-{int(time.time())}"

config = {
    "CallerReference": caller_ref,
    "Comment": "KiranaConnect AI Prototype - HTTPS",
    "Origins": {
        "Quantity": 1,
        "Items": [{
            "Id": "ec2-origin",
            "DomainName": EC2_ORIGIN,
            "CustomOriginConfig": {
                "HTTPPort": 80,
                "HTTPSPort": 443,
                "OriginProtocolPolicy": "http-only",
                "OriginSslProtocols": {"Quantity": 1, "Items": ["TLSv1.2"]}
            }
        }]
    },
    "DefaultCacheBehavior": {
        "TargetOriginId": "ec2-origin",
        "ViewerProtocolPolicy": "redirect-to-https",
        "AllowedMethods": {
            "Quantity": 7,
            "Items": ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"],
            "CachedMethods": {"Quantity": 2, "Items": ["GET", "HEAD"]}
        },
        "ForwardedValues": {
            "QueryString": True,
            "Cookies": {"Forward": "all"},
            "Headers": {"Quantity": 4, "Items": ["Origin", "Content-Type", "Accept", "Authorization"]}
        },
        "MinTTL": 0,
        "DefaultTTL": 0,
        "MaxTTL": 0,
        "Compress": True
    },
    "CacheBehaviors": {
        "Quantity": 2,
        "Items": [
            {
                "PathPattern": "/css/*",
                "TargetOriginId": "ec2-origin",
                "ViewerProtocolPolicy": "redirect-to-https",
                "AllowedMethods": {"Quantity": 2, "Items": ["GET", "HEAD"],
                                   "CachedMethods": {"Quantity": 2, "Items": ["GET", "HEAD"]}},
                "ForwardedValues": {"QueryString": False, "Cookies": {"Forward": "none"}},
                "MinTTL": 86400, "DefaultTTL": 86400, "MaxTTL": 604800, "Compress": True
            },
            {
                "PathPattern": "/js/*",
                "TargetOriginId": "ec2-origin",
                "ViewerProtocolPolicy": "redirect-to-https",
                "AllowedMethods": {"Quantity": 2, "Items": ["GET", "HEAD"],
                                   "CachedMethods": {"Quantity": 2, "Items": ["GET", "HEAD"]}},
                "ForwardedValues": {"QueryString": False, "Cookies": {"Forward": "none"}},
                "MinTTL": 86400, "DefaultTTL": 86400, "MaxTTL": 604800, "Compress": True
            }
        ]
    },
    "Enabled": True,
    "PriceClass": "PriceClass_200",
    "ViewerCertificate": {
        "CloudFrontDefaultCertificate": True,
        "MinimumProtocolVersion": "TLSv1.2_2021"
    },
    "HttpVersion": "http2"
}

try:
    resp = cf.create_distribution(DistributionConfig=config)
    dist = resp["Distribution"]
    domain = dist["DomainName"]
    status = dist["Status"]
    dist_id = dist["Id"]
    print(f"[OK] Distribution created!")
    print(f"  ID:     {dist_id}")
    print(f"  Domain: {domain}")
    print(f"  Status: {status}")
    print(f"")
    print(f"  HTTPS URL: https://{domain}")
    print(f"")
    print(f"  Note: Takes ~5-15 min to deploy globally.")
except Exception as e:
    print(f"[ERR] {e}")
