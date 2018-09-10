from rest_framework.views import exception_handler
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework.exceptions import MethodNotAllowed, AuthenticationFailed, NotAuthenticated


def error_data(__data__: dict = None, **errors):
    for data in errors.items():
        if not isinstance(data[1], list):
            errors.update({data[0]: [data[1]]})
    if __data__ and __data__.get("error"):
        for data in __data__.get("error").items():
            if isinstance(errors.get(data[0]), list):
                try:
                    errors.get(data[0]).extend(data[1])
                except:
                    pass
            else:
                errors.update({data[0]: data[1]})
    return {"error": errors}


def success_data(message: str):
    return {"success": str(message)}


def akaskhoone_rest_framework_exceptions_handler(exc, context):
    response = exception_handler(exc, context)
    if isinstance(exc, InvalidToken):
        response.data = error_data(toke="Invalid")
    elif isinstance(exc, AuthenticationFailed):
        response.data = error_data(toke="Invalid")
    elif isinstance(exc, NotAuthenticated):
        response.data = error_data(toke="Invalid")
    elif isinstance(exc, MethodNotAllowed):
        response.data = error_data(method="Invalid")
    return response
