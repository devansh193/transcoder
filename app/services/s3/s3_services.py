import os
import boto3
import logging
from typing import Dict
from botocore.config import Config
from botocore.exceptions import ClientError

class S3Service:
    def __init__(self, bucket_name: str, region: str):
        if not bucket_name or not region:
            raise ValueError("Bucket name and region are required")
        
        self.bucket_name = bucket_name
        self.s3_client = boto3.client(
            "s3",
            region_name=region,
            config=Config(S3={"addressing_style": "path"})
        )

    def _handle_s3_error(self, error: Exception, context_message: str) -> Exception:
        if isinstance(error, ClientError):
            logging.error(f"S3 Error ({error.response['Error']['Code']}): {error}")
        else:
            logging.error(f"Unknown Error:{error}")
        raise Exception(f"{context_message}:{str(error)}")
    
    def get_url_to_upload(self, key: str, mime_type: str, expires_in: int = 240) -> Dict[str, str]:
        try:
            url = self.s3_client.generate_presigned_url(
                "put_object",
                Params={
                    "Bucket": self.bucket_name,
                    "Key": f"videos/{key}",
                    "ContentType": mime_type
                },
                ExpiresIn= expires_in
            )
            return {"url": url, "path": f"videos/{key}"}
        except Exception as error:
            raise self._handle_s3_error(error, "Failed to generate upload URL")
        
    def get_signed_asset_url(self, key: str, expires_in: int = 14400) -> str:
         try:
             url = self.s3_client.generate_presigned_url(
                 "get_object",
                 Params={
                      "Bucket": self.bucket_name,
                      "Key": key
                  },
                 ExpiresIn=expires_in
             )
             return url
         except Exception as error:
           raise self._handle_s3_error(error, "Failed to generate signed URL")
         
    def download_file(self, key: str, download_path: str) -> str:
        try:
            with open(download_path, "wb") as file:
                self.s3_client.download_fileObj(self.bucket_name, key, file)
            return download_path
        except Exception as error:
            raise self._handle_s3_error(error, f"Failed to download file {key}")
