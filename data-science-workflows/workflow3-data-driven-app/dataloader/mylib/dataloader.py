import boto3
import logging
from botocore.exceptions import ClientError
import os


def upload_data_spaces(filename, spacename):
    os.chdir("data/")
    session = boto3.session.Session()
    client = session.client(
        "s3",
        endpoint_url=os.environ["ENDPOINT_URL"],
        region_name="",
        aws_access_key_id=os.environ["SPACES_ID"],
        aws_secret_access_key=os.environ["SECRET_KEY"],
    )
    try:
        client.upload_file(filename, spacename, filename)
    except ClientError as e:
        logging.error(e)
        return False
    return True
