import hashlib
import logging
from logging.config import dictConfig

import boto3 as boto3
from configs.configs import aws_access_key, aws_secret_key, aws_bucket_name

log = logging.getLogger('file')

mongo_instance = None

class DatasetUtils:
    def __init__(self):
        pass

    # Utility to get tags out of an object
    def get_tags(self, d):
        for v in d.values():
            if isinstance(v, dict):
                yield from self.get_tags(v)
            elif isinstance(v, list):
                for entries in v:
                    yield entries
            else:
                yield v

    # Utility to hash a file
    def hash_file(self, filename):
        h = hashlib.sha256()
        try:
            with open(filename, 'rb') as file:
                chunk = 0
                while chunk != b'':
                    chunk = file.read(1024)
                    h.update(chunk)
            return h.hexdigest()
        except Exception as e:
            log.exception(e)
            return None

    # Utility to upload files to ULCA S3 Bucket
    def upload_file(self, file_name, s3_file_name):
        if s3_file_name is None:
            s3_file_name = file_name
        s3_client = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key)
        try:
            response = s3_client.upload_file(file_name, aws_bucket_name, s3_file_name)
            return response
        except Exception as e:
            log.exception(e)
            return False

    # Utility to download files to ULCA S3 Bucket
    def download_file(self, s3_file_name):
        s3_client = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key)
        try:
            response = s3_client.download_file(aws_bucket_name, s3_file_name)
            return response
        except Exception as e:
            log.exception(e)
            return False

# Log config
dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] {%(filename)s:%(lineno)d} %(threadName)s %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {
        'info': {
            'class': 'logging.FileHandler',
            'level': 'DEBUG',
            'formatter': 'default',
            'filename': 'info.log'
        },
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'default',
            'stream': 'ext://sys.stdout',
        }
    },
    'loggers': {
        'file': {
            'level': 'DEBUG',
            'handlers': ['info', 'console'],
            'propagate': ''
        }
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['info', 'console']
    }
})