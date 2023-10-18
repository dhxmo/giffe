import os

from dotenv import load_dotenv
load_dotenv()


class Config:
    s3_giffe_access_key = os.environ['s3_giffe_access_key']
    s3_secret_access_key = os.environ['s3_secret_access_key']
    s3_bucket_name = os.environ['s3_bucket_name']