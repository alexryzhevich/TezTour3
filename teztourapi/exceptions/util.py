from .structs import ErrorMessage
from .exceptions import PARSE_ERROR_CODE


def message_from_serializer_errors(errors):
    messages = []
    for key in errors:
        for message in errors[key]:
            messages.append(key.capitalize() + ': ' + message)
    return ErrorMessage(PARSE_ERROR_CODE, ' '.join(messages))
