from botocore.exceptions import ClientError
from django.http import HttpResponse

import boto3
import os


def sendfile(request, filename, **kwargs):
    print(filename)
    response = HttpResponse()
    s3 = boto3.client(
        service_name='s3',
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID', 'your-spaces-access-key-id'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY', 'your-spaces-secret-access-key'),
        endpoint_url=os.environ.get('AWS_S3_ENDPOINT_URL', 'your-spaces-endpoint-url'),
    )
    try:
        presigned_url = s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': os.environ.get('AWS_STORAGE_BUCKET_NAME', 'your-spaces-bucket-name'),
                'Key': filename,

            },
            ExpiresIn= 60*30
        )
        response['X-Accel-Redirect'] = presigned_url
        return response
    except ClientError as e:
        print(e)
        return HttpResponse(status=404)
