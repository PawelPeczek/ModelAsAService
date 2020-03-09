from dataclasses import dataclass
from enum import Enum
from typing import Dict


@dataclass
class ServiceSpecs:
    host: str
    port: int
    service_name: str


class Service(Enum):
    DISCOVERY_SERVICE = 0
    SERVER_IDENTITY_SERVICE = 1
    USER_IDENTITY_SERVICE = 2
    RESOURCES_MANAGER_SERVICE = 3
    PEOPLE_DETECTION_SERVICE = 4
    FACE_DETECTION_SERVICE = 5
    AGE_ESTIMATION_SERVICE = 6


ServicesSpecs = Dict[Service, ServiceSpecs]


@dataclass
class ServiceJWT:
    token: str
    token_secret: str
