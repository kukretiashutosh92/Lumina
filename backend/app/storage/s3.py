"""
file handles:
- Upload file to S3
- Download file from S3
- Delete file from S3
"""

import asyncio
from app.config import settings
from app.storage.base import StorageBackend


class S3Storage(StorageBackend):

    def __init__(self):
        # Make sure bucket name is set
        if not settings.aws_bucket:
            raise ValueError("AWS bucket name is missing")

        self.bucket = settings.aws_bucket
        self.region = settings.aws_region or "us-east-1"

    # Create S3 client
    def get_client(self):
        import boto3
        return boto3.client("s3", region_name=self.region)

    # -------------------------
    # Upload File
    # -------------------------
    async def put(self, key, content, content_type=""):
        """
        Upload file to S3
        key = filename in S3
        content = file object
        """

        client = self.get_client()

        # Read file content
        body = content.read()

        # Run blocking S3 call in background thread
        await asyncio.to_thread(
            client.put_object,
            Bucket=self.bucket,
            Key=key,
            Body=body,
            ContentType=content_type or "application/octet-stream",
        )

        return key

    # -------------------------
    # Download File
    # -------------------------
    async def get(self, key):
        """
        Download file from S3
        Returns file content (bytes)
        """

        from botocore.exceptions import ClientError

        client = self.get_client()

        try:
            response = await asyncio.to_thread(
                client.get_object,
                Bucket=self.bucket,
                Key=key,
            )

            return response["Body"].read()

        except ClientError:
            # File not found
            return None

    # -------------------------
    # Delete File
    # -------------------------
    async def delete(self, key):
        """
        Delete file from S3
        """

        client = self.get_client()

        try:
            await asyncio.to_thread(
                client.delete_object,
                Bucket=self.bucket,
                Key=key
            )
            return True
        except:
            return False