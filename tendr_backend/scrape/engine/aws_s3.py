import boto3
import environ

from tendr_backend.scrape.engine.local import delete_file

env = environ.Env()

AWS_ACCESS_KEY_ID = env.str("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = env.str("AWS_SECRET_ACCESS_KEY", "")
REGION_NAME = env.str("REGION_NAME", "")
BUCKET_NAME = env.str("BUCKET_NAME", "")

# Initialize the S3 client
s3 = boto3.client(
    "s3", aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name=REGION_NAME
)


def upload_to_s3(local_file_path, s3_key):
    try:
        # Upload file to S3 bucket
        s3.upload_file(local_file_path, BUCKET_NAME, s3_key)
        print(f"File uploaded successfully to S3 with key: {s3_key}")
    except Exception as e:
        print(f"Error uploading file to S3: {e}")
    finally:
        delete_file(local_file_path)


def download_from_s3(s3_key, local_file_path):
    try:
        # Download file from S3 bucket
        s3.download_file(BUCKET_NAME, s3_key, local_file_path)
        print(f"File downloaded successfully to local path: {local_file_path}")
    except Exception as e:
        print(f"Error downloading file from S3: {e}")


def delete_from_s3(s3_key):
    try:
        # Delete file from S3 bucket
        s3.delete_object(Bucket=BUCKET_NAME, Key=s3_key)
        print(f"File deleted successfully from S3 with key: {s3_key}")
    except Exception as e:
        print(f"Error deleting file from S3: {e}")


# examples
# Local file path to upload
# local_upload_file_path = 'setup.cfg'
# s3_upload_key = 'cft-files/file.cfg'  # The S3 object key (file path inside the bucket)

# # Local file path to save the downloaded file
# local_download_file_path = 'a.py'
# s3_download_key = 'cft-files/file.py'  # The S3 object key (file path inside the bucket)

# Upload file to S3
# upload_to_s3(local_upload_file_path, s3_upload_key)

# # Download file from S3
# download_from_s3(s3_download_key, local_download_file_path)


# # Delete file from S3
# delete_from_s3(s3_upload_key)
