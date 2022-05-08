import boto3
import logging
from botocore.exceptions import ClientError
import os


def download_file_s3(filename):
    """Helper function that allows you to download data from object storage specifically S3 by providing the filename

    Parameters
    ----------
    filename : this is the name of the file you want to download from spaces


    Returns
    -------
    Boolean True/False
    True if your file downloaded.
    False file didn't download with an arror message.
    A file in different formats CSV and or PNG.

    NB: You need to have stored the endpointurl, region_name, aws_access_key_id, and aws_secret_access_key and spaces name from Digital ocean
    as environment variables e.g export SPACES_NAME=<stuff>

    Example
    -------
    download_file_s3(chowder.txt) downloads a file in the available folder chowder.txt

    """
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
        client.download_file(os.environ["SPACES_NAME"], filename, filename)
    except ClientError as e:
        logging.error(e)
        return False
    return True


def upload_data_spaces(filename):
    """helper that allows you to upload data to object storage specifically Digital Ocean Spaces

    Parameters
    ----------
    filename : this is the name of the file you want to upload from your working directory. Any file format works.
    Object storage is not picky.


    Returns
    -------
    Boolean True/False
    True if your file uploaded.
    False file didn't upload with an arror message.

    NB: You need to have stored the endpointurl, region_name, aws_access_key_id, and aws_secret_access_key and spaces name from Digital ocean
    as environment variables e.g export SPACES_NAME=<stuff>

    Example
    -------
    upload_data_spaces(chowder.txt) uploads a file in the available folder chowder.txt
    """
    session = boto3.session.Session()
    client = session.client(
        "s3",
        endpoint_url=os.environ["ENDPOINT_URL"],
        region_name="ams3",
        aws_access_key_id=os.environ["SPACES_ID"],
        aws_secret_access_key=os.environ["SECRET_KEY"],
    )
    try:
        client.upload_file(filename, os.environ["SPACES_NAME"], filename)
    except ClientError as e:
        logging.error(e)
        return False
    return True
