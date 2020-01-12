from enum import Enum


class Privilege(Enum):
    ASYNCHRONOUS_USER = 1
    SYNCHRONOUS_USER = 2
    ADMIN = 3
    SUPER_USER = 4
