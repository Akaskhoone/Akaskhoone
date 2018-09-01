from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.settings import api_settings


class APIJWTClient(APIClient):
    def login(self, url="/api/v0/accounts/login/", get_response=True, token="access", auth_header_type=0, **credentials):
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
