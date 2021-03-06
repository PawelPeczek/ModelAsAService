import os

from config_generation_utils import dump_json_file, fetch_from_env

TARGET_FILE_PATH = os.path.join("./server_identity_service/db_content.json")

TO_FETCH_FROM_ENV = [
    ('AGE_ESTIMATION_SERVICE_NAME', 'AGE_ESTIMATION_SERVICE_SECRET'),
    ('DISCOVERY_SERVICE_NAME', 'DISCOVERY_SERVICE_SECRET'),
    ('FACE_DETECTION_SERVICE_NAME', 'FACE_DETECTION_SERVICE_SECRET'),
    ('GATEWAY_SERVICE_NAME', 'GATEWAY_SERVICE_SECRET'),
    ('PEOPLE_DETECTION_SERVICE_NAME', 'PEOPLE_DETECTION_SERVICE_SECRET'),
    ('RESOURCES_MANAGER_SERVICE_NAME', 'RESOURCES_MANAGER_SERVICE_SECRET'),
    ('USER_IDENTITY_SERVICE_NAME', 'USER_IDENTITY_SERVICE_SECRET')
]


def create_db_content() -> None:
    env_content = fetch_from_env(to_fetch=TO_FETCH_FROM_ENV)
    config_file_content = [
        {'service_name': service_name, 'service_password': service_password}
        for (service_name, service_password) in env_content
    ]
    dump_json_file(path=TARGET_FILE_PATH, content=config_file_content)


if __name__ == '__main__':
    create_db_content()
