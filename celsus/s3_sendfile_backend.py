from rest_framework import status
from rest_framework.response import Response

def sendfile(request, filename, **kwargs):
    headers = {'Location': filename, 'Access-Control-Allow-Origin': request.headers['Origin']}
    print(headers)
    return Response(status=status.HTTP_303_SEE_OTHER, headers=headers)