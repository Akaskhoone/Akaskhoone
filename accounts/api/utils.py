from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.settings import api_settings
from django.contrib.auth import get_user_model

User = get_user_model()


def get_user(request):
    username = request.query_params.get('username')
    if username:
        try:
            return User.objects.get(username=username)
        except:
            return None
    email = request.query_params.get('email')
    if email:
        try:
            return User.objects.get(email=email)
        except:
            return None
    return request.user


def get_password_errors(e):
    errors = []
    for i in e.args[0]:
        if str(list(i)[0]).__contains__('similar'):
            errors.append("Similar")
        elif str(list(i)[0]).__contains__('short'):
            errors.append("Length")
        elif str(list(i)[0]).__contains__('numeric'):
            errors.append("Numeric")
        elif str(list(i)[0]).__contains__('common'):
            errors.append("Common")
    return errors


class APIJWTClient(APIClient):
    def login(self, url="/api/v0/accounts/login/", get_response=True, token="access", auth_header_type=0,
              **credentials):
        auth_header_type = auth_header_type if auth_header_type < len(api_settings.AUTH_HEADER_TYPES) else 0
        response = self.post(path=url, data=credentials, format='json')
        if response.status_code == status.HTTP_200_OK:
            self.credentials(
                HTTP_AUTHORIZATION="{0} {1}".format(
                    api_settings.AUTH_HEADER_TYPES[auth_header_type] if isinstance(auth_header_type,
                                                                                   int) else auth_header_type,
                    response.data[token]))
            return (True, response) if get_response else True
        else:
            return (False, response) if get_response else False


class APIJWTTestCase(APITestCase):
    client_class = APIJWTClient
