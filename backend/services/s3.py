"""S3 service — handles file uploads to Amazon S3 (stubbed for local dev)."""

import boto3
from botocore.exceptions import ClientError
from backend.config import AWS_REGION, S3_BUCKET, USE_LOCAL_DATA


def get_s3_client():
    """Get S3 client."""
    if USE_LOCAL_DATA:
        return None
    return boto3.client('s3', region_name=AWS_REGION)


def upload_file(file_bytes: bytes, key: str, content_type: str = "image/jpeg") -> str:
    """Upload a file to S3 and return the URL."""
    if USE_LOCAL_DATA:
        return f"https://{S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{key}"

    client = get_s3_client()
    try:
        client.put_object(
            Bucket=S3_BUCKET,
            Key=key,
            Body=file_bytes,
            ContentType=content_type
        )
        return f"https://{S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{key}"
    except ClientError as e:
        raise Exception(f"S3 upload failed: {e}")


def get_file_url(key: str) -> str:
    """Get a presigned URL for a file."""
    if USE_LOCAL_DATA:
        return f"https://{S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{key}"

    client = get_s3_client()
    try:
        url = client.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET, 'Key': key},
            ExpiresIn=3600
        )
        return url
    except ClientError as e:
        raise Exception(f"S3 URL generation failed: {e}")
