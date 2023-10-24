import os

from dotenv import load_dotenv
load_dotenv()


class Config:
    s3_giffe_access_key = os.environ['s3_giffe_access_key']
    s3_secret_access_key = os.environ['s3_secret_access_key']
    s3_bucket_name = os.environ['s3_bucket_name']
    insta_username = os.environ['insta_username']
    insta_password = os.environ['insta_password']