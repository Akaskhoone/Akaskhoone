from rest_framework.views import exception_handler
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework.exceptions import MethodNotAllowed, AuthenticationFailed, NotAuthenticated


def error_data(__data__=None, **errors):
    error = {}
    for data in errors.items():
        key = str(data[0]).lower()
        error_list = []
        if not isinstance(data[1], list):
            error_list.append(str(data[1]).title().replace(" ", ""))
        else:
            for err in data[1]:
                error_list.append(str(err).title().replace(" ", ""))
        error.update({
            key: error_list
        })
    if __data__:
        for data in __data__.get("error").items():
            if error.get(data[0]):
                try:
                    error.get(data[0]).extend(data[1])
                    data_list = set(error.get(data[0]))
                    error.update({data[0]: list(data_list)})
                except:
                    pass
            else:
                error.update({data[0]: data[1]})
    return {"error": error}


def success_data(message: str):
    return {"success": str(message).title().replace(" ", "")}


def akaskhoone_rest_framework_exceptions_handler(exc, context):
    data = error_data(make="new", data_assets=["one", "two", "three oNE"])
    data = error_data(madam=["fUck Uede"], make=["one"])
    print(error_data(__data__=data, madam=["fUck Uede"], make=["two"]))
    response = exception_handler(exc, context)
    if isinstance(exc, InvalidToken):
        response.data = {"error": {"token": ["Invalid"]}}
    elif isinstance(exc, MethodNotAllowed):
        response.data = error_data(make="new", data=["one", "two", "three"])
    elif isinstance(exc, AuthenticationFailed):
        response.data = {"error": {"authorization": ["Invalid"]}}
    elif isinstance(exc, NotAuthenticated):
        response.data = {"error": {"authentication": ["Invalid"]}}
    return response
