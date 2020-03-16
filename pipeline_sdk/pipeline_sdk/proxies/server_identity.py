import requests

from .errors import IdentityVerificationFailed, RequestProcessingError
from ..config import VERIFY_SERVICE_IDENTITY_PATH
from .primitives import ServiceSpecs, ServiceJWT
from ..utils import compose_url


class ServerIdentityClient:

    def __init__(self, server_identity_specs: ServiceSpecs):
        self.__server_identity_specs = server_identity_specs

    def obtain_service_jwt(self,
                           service_name: str,
                           service_secret: str
                           ) -> ServiceJWT:
        url = compose_url(
            service_specs=self.__server_identity_specs,
            path_postfix=VERIFY_SERVICE_IDENTITY_PATH
        )
        payload = {'service_name': service_name, 'password': service_secret}
        response = requests.get(url, json=payload, verify=False)
        if response.status_code == 200:
            content = response.json()
            return ServiceJWT(
                token=content['service_access_token'],
                token_secret=content['token_secret']
            )
        elif response.status_code == 401:
            content = response.json()
            raise IdentityVerificationFailed(content['msg'])
        else:
            raise RequestProcessingError(
                f'Error code: {response.status_code}, Cause: {response.text}'
            )
