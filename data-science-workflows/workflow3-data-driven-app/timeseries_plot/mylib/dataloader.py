import boto3
import logging
from botocore.exceptions import ClientError
import os


def download_file_s3(spacename, filename):
    os.getcwd()
    session = boto3.session.Session()  # initiate session
    # use aws sdk to define credentials to access service
    client = session.client(
        "s3",
        endpoint_url=os.environ["ENDPOINT_URL"],
        region_name="ams3",
        aws_access_key_id=os.environ["SPACES_ID"],
        aws_secret_access_key=os.environ["SECRET_KEY"],
    )
    try:
        client.download_file(spacename, filename, filename)
    except ClientError as e:
        logging.error(e)
        return False
    return True


def upload_data_spaces(filename, spacename):
    session = boto3.session.Session()
    client = session.client(
        "s3",
        endpoint_url=os.environ["ENDPOINT_URL"],
        region_name="ams3",
        aws_access_key_id=os.environ["SPACES_ID"],
        aws_secret_access_key=os.environ["SECRET_KEY"],
    )
    try:
        client.upload_file(filename, spacename, filename)
    except ClientError as e:
        logging.error(e)
        return False
    return True
