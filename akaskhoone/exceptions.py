from rest_framework.views import exception_handler
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework.exceptions import MethodNotAllowed, AuthenticationFailed, NotAuthenticated
from .utils import error_data


def akaskhoone_rest_framework_exceptions_handler(exc, context):
    response = exception_handler(exc, context)
    if isinstance(exc, InvalidToken):
        response.data = error_data(token="Invalid")
    elif isinstance(exc, AuthenticationFailed):
        response.data = error_data(token="Invalid")
    elif isinstance(exc, NotAuthenticated):
        response.data = error_data(token="Invalid")
    elif isinstance(exc, MethodNotAllowed):
        response.data = error_data(method="Invalid")
    return response
