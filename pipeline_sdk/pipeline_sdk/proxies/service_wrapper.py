# from typing import Dict, List
#
# import requests
#
# from pipeline_sdk.pipeline_sdk.utils import compose_url
# from .errors import ServiceSpecsNotProvided, IdentityVerificationFailed, \
#     RequestProcessingError
# from .primitives import ServicesSpecs, ServiceJWT, Service, ServiceSpecs
#
#
# class ServiceClient:
#
#     def __init__(self,
#                  services_specs: ServicesSpecs,
#                  service_name: str,
#                  service_secret: str
#                  ):
#         self.__services_specs = services_specs
#         self.__service_name = service_name
#         self.__service_secret = service_secret
#         self.__service_token = None
#
#     def obtain_identity_jwt(self) -> ServiceJWT:
#         identity_jwt = self.obtain_service_jwt(
#             service_name=self.__service_name,
#             service_secret=self.__service_secret
#         )
#         self.__service_token = identity_jwt.token
#         return identity_jwt
#
#     def obtain_service_jwt(self,
#                           service_name: str,
#                            service_secret: str
#                            ) -> ServiceJWT:
#         url = self.__get_url(service=Service.SERVER_IDENTITY_SERVICE)
#         payload = {'service_name': service_name, 'password': service_secret}
#         response = requests.get(url, json=payload, verify=False)
#         if response.status_code == 200:
#             content = response.json()
#             return ServiceJWT(
#                 token=content['service_access_token'],
#                 token_secret=content['token_secret']
#             )
#         elif response.status_code == 401:
#             content = response.json()
#             raise IdentityVerificationFailed(content['msg'])
#         else:
#             raise RequestProcessingError(
#                 f'Error code: {response.status_code}, Cause: {response.text}'
#             )
#
#     def obtain_discovery_info(self,
#                               service_names: List[str]
#                               ) -> Dict[str, ServiceSpecs]:
#         url = self.__get_url(service=Service.DISCOVERY_SERVICE)
#         if self.__service_token is None:
#             service_jwt = self.obtain_identity_jwt()
#             self.__service_token = service_jwt.token
#         headers = {'Authorization': f'Bearer {self.__service_token}'}
#         payload = {'service_names': service_names}
#         response = requests.get(url, headers=headers, json=payload, verify=False)
#         if response.status_code == 200:
#             return self.__handle
#             response_content = response.json()
#             services_found = response_content.get('services_found', [])
#             return {
#                 service['service_name']: ServiceSpecs(
#                     host=service['service_address'],
#                     port=int(service['service_port']),
#                     service_name=service['service_name']
#                 )
#                 for service in services_found
#             }
#
#     def __get_url(self, service: Service) -> str:
#         service_specs = self.__services_specs.get(service)
#         if service_specs is None:
#             raise ServiceSpecsNotProvided(
#                 f"{Service.SERVER_IDENTITY_SERVICE.name} service specs not set."
#             )
#         return compose_url(
#             service_specs=service_specs,
#             path_postfix='verify_service_identity'
#         )
