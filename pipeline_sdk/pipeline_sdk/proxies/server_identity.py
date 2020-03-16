import logging
import time

import requests
from requests import RequestException

from .errors import IdentityVerificationFailed, RequestProcessingError
from ..config import VERIFY_SERVICE_IDENTITY_PATH, LOGGING_LEVEL
from .primitives import ServiceSpecs, ServiceJWT

logging.getLogger().setLevel(LOGGING_LEVEL)


class ServerIdentityClient:

    def __init__(self, server_identity_specs: ServiceSpecs):
        self.__server_identity_specs = server_identity_specs

    def obtain_service_jwt_safely(self,
                                  service_name: str,
                                  service_secret: str
                                  ) -> ServiceJWT:
        while True:
            try:
                return self.obtain_service_jwt(
                    service_name=service_name,
                    service_secret=service_secret
                )
            except (RequestException, ConnectionError) as e:
                logging.error(f"Could not obtain JWT: {e}")
                time.sleep(5)

    def obtain_service_jwt(self,
                           service_name: str,
                           service_secret: str
                           ) -> ServiceJWT:
        from ..utils import compose_url
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
