from rest_framework.views import exception_handler as default_handler

from .exceptions import PARSE_ERROR_CODE
from .serializers import ErrorMessageSerializer
from .structs import ErrorMessage


def exception_handler(exc, context):
    response = default_handler(exc, context)

    if response is not None:
        message = response.data['detail'] if 'detail' in response.data else None
        response.data = ErrorMessageSerializer(ErrorMessage(PARSE_ERROR_CODE, message)).data

    return response
