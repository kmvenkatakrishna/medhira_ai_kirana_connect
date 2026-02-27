import os
import boto3
import uuid
from datetime import datetime

MEDIA_BUCKET_NAME = os.environ.get("MEDIA_BUCKET", "kirana-media-bucket")

# Local testing support
s3_url = os.environ.get("S3_URL", None)
if s3_url:
    s3_client = boto3.client('s3', endpoint_url=s3_url)
else:
    s3_client = boto3.client('s3')

class MediaService:
    @staticmethod
    def generate_presigned_upload_url(store_id: str, filename: str, content_type: str, expiration: int = 3600):
        """Generate a presigned URL to upload a file directly to S3 from frontend"""
        extension = filename.split('.')[-1] if '.' in filename else ''
        file_key = f"stores/{store_id}/receipts/{datetime.utcnow().strftime('%Y-%m-%d')}/{uuid.uuid4()}.{extension}"
        
        try:
            response = s3_client.generate_presigned_post(
                Bucket=MEDIA_BUCKET_NAME,
                Key=file_key,
                Fields={"Content-Type": content_type},
                Conditions=[{"Content-Type": content_type}],
                ExpiresIn=expiration
            )
            return {
                "url": response["url"],
                "fields": response["fields"],
                "file_key": file_key
            }
        except Exception as e:
            print(f"Error generating presigned upload url: {e}")
            raise e

    @staticmethod
    def get_presigned_download_url(file_key: str, expiration: int = 3600):
        """Generate a presigned URL to securely download/view a file"""
        try:
            response = s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': MEDIA_BUCKET_NAME,
                    'Key': file_key
                },
                ExpiresIn=expiration
            )
            return response
        except Exception as e:
            print(f"Error generating presigned download url: {e}")
            raise e
