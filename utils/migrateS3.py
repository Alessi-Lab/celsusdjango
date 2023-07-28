import os

import boto3
from botocore.exceptions import ClientError
from celsus.models import Curtain
s3 = boto3.resource(
    service_name='s3',
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID', 'your-spaces-access-key-id'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY', 'your-spaces-secret-access-key'),
    endpoint_url=os.environ.get('AWS_S3_ENDPOINT_URL', 'your-spaces-endpoint-url'),
)
if __name__ == '__main__':

    allSessions = Curtain.objects.all()
    for session in allSessions:
        filename = session.file.name
        try:
            res = s3.Object(
                os.environ.get('AWS_STORAGE_BUCKET_NAME', 'your-spaces-bucket-name'),
                filename).get()
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                with open(filename, 'rb') as data:
                    session.file.save(session.file.name.replace("media/files/curtain_upload"), data)
            else:
                raise
