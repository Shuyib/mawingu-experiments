import boto3
import logging
from botocore.exceptions import ClientError
from botocore.config import Config
import os
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def validate_env_vars():
    """Validate required environment variables are set
    
    Returns
    -------
    Boolean True/False
    True if all required environment variables are set.
    False if any required environment variables are missing.
    
    """
    required_vars = ['ENDPOINT_URL', 'SECRET_KEY', 'SPACES_ID', 'SPACES_NAME']
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        error_msg = f"Missing required environment variables: {', '.join(missing)}"
        logger.error(error_msg)
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
    False file didn't upload with an error message.

    NB: You need to have stored the endpointurl, region_name, aws_access_key_id, and aws_secret_access_key and spaces name from Digital ocean
    as environment variables e.g export SPACES_NAME=<nameofspace>

    Example
    -------
    upload_data_spaces(chowder.txt) uploads a file in the available folder chowder.txt


    """
    # Validate environment variables
    if not validate_env_vars():
        logger.error("Cannot proceed with upload: missing environment variables")
        return False
    
    # Validate file exists before upload
    if not os.path.isfile(filename):
        logger.error(f"File not found: {filename}")
        return False
    
    # Configure retry logic with exponential backoff
    config = Config(
        retries={
            'max_attempts': 3,
            'mode': 'standard'
        },
        connect_timeout=10,
        read_timeout=30
    )
    
    session = boto3.session.Session()
    client = session.client(
        "s3",
        endpoint_url=os.getenv("ENDPOINT_URL"),
        region_name="ams3",
        aws_access_key_id=os.getenv("SPACES_ID"),
        aws_secret_access_key=os.getenv("SECRET_KEY"),
        config=config
    )
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            client.upload_file(filename, os.getenv("SPACES_NAME"), filename)
            logger.info(f"Successfully uploaded {filename} to {os.getenv('SPACES_NAME')}")
            return True
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            error_msg = e.response.get('Error', {}).get('Message', str(e))
            logger.error(f"S3 upload attempt {attempt + 1}/{max_retries} failed - Code: {error_code}, Message: {error_msg}")
            
            if attempt < max_retries - 1:
                # Exponential backoff
                wait_time = 2 ** attempt
                logger.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                logger.error(f"Failed to upload {filename} after {max_retries} attempts")
                return False
        except Exception as e:
            logger.error(f"Unexpected error uploading {filename}: {e}")
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                logger.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                return False
    
    return False
