import os
from s3_services import S3Service 

BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")
REGION = os.getenv("AWS_REGION")
if not BUCKET_NAME or not REGION:
    raise ValueError("AWS_BUCKET_NAME and AWS_REGION must be defined in environment variables")
s3_driver = S3Service(bucket_name=BUCKET_NAME, region=REGION)
