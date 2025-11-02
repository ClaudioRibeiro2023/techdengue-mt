"""
S3 Service - Handles S3 operations for evidence storage
"""
import os
import uuid
from typing import Dict, Optional
from datetime import datetime, timedelta
import boto3
from botocore.exceptions import ClientError
from botocore.client import Config


class S3Service:
    """Service for S3 operations (presigned URLs, uploads, etc)"""
    
    def __init__(
        self,
        endpoint_url: Optional[str] = None,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        bucket_name: Optional[str] = None,
        region: str = "us-east-1"
    ):
        """
        Initialize S3 service.
        
        Args:
            endpoint_url: S3 endpoint (MinIO for dev, AWS for prod)
            access_key: S3 access key
            secret_key: S3 secret key
            bucket_name: Default bucket name
            region: AWS region
        """
        self.endpoint_url = endpoint_url or os.getenv("S3_ENDPOINT", "http://minio:9000")
        self.access_key = access_key or os.getenv("S3_ACCESS_KEY", "minioadmin")
        self.secret_key = secret_key or os.getenv("S3_SECRET_KEY", "minioadmin")
        self.bucket_name = bucket_name or os.getenv("S3_BUCKET_EVIDENCIAS", "techdengue-evidencias")
        self.region = region
        
        # Initialize boto3 client
        self.client = boto3.client(
            's3',
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region,
            config=Config(signature_version='s3v4')
        )
    
    def generate_presigned_upload_url(
        self,
        atividade_id: int,
        filename: str,
        content_type: str,
        expires_in: int = 300
    ) -> Dict[str, str]:
        """
        Generate presigned URL for direct upload to S3.
        
        Args:
            atividade_id: Activity ID (for folder organization)
            filename: Original filename
            content_type: MIME type
            expires_in: URL validity in seconds (default 5 minutes)
            
        Returns:
            Dict with upload_url, upload_id, and object_key
        """
        # Generate unique upload ID
        upload_id = str(uuid.uuid4())
        
        # Build S3 object key: atividades/{atividade_id}/{upload_id}_{filename}
        safe_filename = self._sanitize_filename(filename)
        object_key = f"atividades/{atividade_id}/{upload_id}_{safe_filename}"
        
        try:
            # Generate presigned URL for PUT operation
            presigned_url = self.client.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': object_key,
                    'ContentType': content_type
                },
                ExpiresIn=expires_in,
                HttpMethod='PUT'
            )
            
            return {
                "upload_url": presigned_url,
                "upload_id": upload_id,
                "object_key": object_key,
                "expires_in": expires_in
            }
        except ClientError as e:
            raise Exception(f"Failed to generate presigned URL: {str(e)}")
    
    def generate_presigned_download_url(
        self,
        object_key: str,
        expires_in: int = 3600
    ) -> str:
        """
        Generate presigned URL for download from S3.
        
        Args:
            object_key: S3 object key
            expires_in: URL validity in seconds (default 1 hour)
            
        Returns:
            Presigned download URL
        """
        try:
            presigned_url = self.client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': object_key
                },
                ExpiresIn=expires_in,
                HttpMethod='GET'
            )
            return presigned_url
        except ClientError as e:
            raise Exception(f"Failed to generate download URL: {str(e)}")
    
    def check_object_exists(self, object_key: str) -> bool:
        """
        Check if object exists in S3.
        
        Args:
            object_key: S3 object key
            
        Returns:
            True if exists, False otherwise
        """
        try:
            self.client.head_object(Bucket=self.bucket_name, Key=object_key)
            return True
        except ClientError:
            return False
    
    def get_object_metadata(self, object_key: str) -> Optional[Dict]:
        """
        Get object metadata from S3.
        
        Args:
            object_key: S3 object key
            
        Returns:
            Dict with metadata or None if not found
        """
        try:
            response = self.client.head_object(Bucket=self.bucket_name, Key=object_key)
            return {
                "content_type": response.get("ContentType"),
                "content_length": response.get("ContentLength"),
                "last_modified": response.get("LastModified"),
                "etag": response.get("ETag", "").strip('"'),
                "metadata": response.get("Metadata", {})
            }
        except ClientError:
            return None
    
    def delete_object(self, object_key: str) -> bool:
        """
        Delete object from S3.
        
        Args:
            object_key: S3 object key
            
        Returns:
            True if deleted, False if not found
        """
        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=object_key)
            return True
        except ClientError:
            return False
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename for S3 storage.
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        # Remove path traversal attempts
        filename = os.path.basename(filename)
        
        # Replace spaces and special characters
        filename = filename.replace(" ", "_")
        filename = "".join(c for c in filename if c.isalnum() or c in "._-")
        
        # Limit length
        if len(filename) > 200:
            name, ext = os.path.splitext(filename)
            filename = name[:190] + ext
        
        return filename
