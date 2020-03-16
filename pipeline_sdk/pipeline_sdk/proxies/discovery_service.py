from typing import Dict, List

import requests
from flask import Response
from .primitives import ServiceSpecs
from .errors import IdentityVerificationFailed, RequestProcessingError
from ..config import LOCATE_SERVICES_PATH


class DiscoveryServiceClient:

    def __init__(self,
                 discovery_service_specs: ServiceSpecs,
                 service_token: str
                 ):
        self.__discovery_service_specs = discovery_service_specs
        self.__service_token = service_token

    def obtain_discovery_info(self,
                              service_names: List[str]
                              ) -> Dict[str, ServiceSpecs]:
        from ..utils import compose_url
        url = compose_url(
            service_specs=self.__discovery_service_specs,
            path_postfix=LOCATE_SERVICES_PATH
        )
        headers = {'Authorization': f'Bearer {self.__service_token}'}
        payload = {'service_names': service_names}
        response = requests.get(
            url, headers=headers, json=payload, verify=False
        )
        if response.status_code == 200:
            return self.__produce_output_from_successful_response(
                response=response
            )
        elif response.status_code == 401:
            content = response.json()
            raise IdentityVerificationFailed(content['msg'])
        else:
            raise RequestProcessingError(
                f'Error code: {response.status_code}, Cause: {response.text}'
            )

    def __produce_output_from_successful_response(self,
                                                  response: Response
                                                  ) -> Dict[str, ServiceSpecs]:
        response_content = response.json()
        services_found = response_content.get('services_found', [])
        return {
            service['service_name']: ServiceSpecs(
                host=service['service_address'],
                port=int(service['service_port']),
                service_name=service['service_name']
            )
            for service in services_found
        }
