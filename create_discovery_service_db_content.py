import os

from config_generation_utils import dump_json_file, fetch_from_env

TARGET_FILE_PATH = os.path.join("./discovery_service/db_content.json")

BATCH_INPUT = [
    (
        'AGE_ESTIMATION_SERVICE_NAME',
        'AGE_ESTIMATION_SERVICE_HOST',
        'AGE_ESTIMATION_SERVICE_PORT'
    ),
    (
        'DISCOVERY_SERVICE_NAME',
        'DISCOVERY_SERVICE_HOST',
        'DISCOVERY_SERVICE_PORT'
    ),
    (
        'FACE_DETECTION_SERVICE_NAME',
        'FACE_DETECTION_SERVICE_HOST',
        'FACE_DETECTION_SERVICE_PORT'
    ),
    (
        'GATEWAY_SERVICE_NAME',
        'GATEWAY_SERVICE_HOST',
        'GATEWAY_SERVICE_PORT'
    ),
    (
        'PEOPLE_DETECTION_SERVICE_NAME',
        'PEOPLE_DETECTION_SERVICE_HOST',
        'PEOPLE_DETECTION_SERVICE_PORT'
    ),
    (
        'RESOURCES_MANAGER_SERVICE_NAME',
        'RESOURCES_MANAGER_SERVICE_HOST',
        'RESOURCES_MANAGER_SERVICE_PORT'
    ),
    (
        'USER_IDENTITY_SERVICE_NAME',
        'USER_IDENTITY_SERVICE_HOST',
        'USER_IDENTITY_SERVICE_PORT'
    ),
    (
        'MESSAGE_BROKER_NAME',
        'MESSAGE_BROKER_HOST',
        'MESSAGE_BROKER_PORT'
    )
]


def create_db_content() -> None:
    env_content = fetch_from_env(to_fetch=BATCH_INPUT)
    config_file_content = [
        {'service_name': name, 'service_host': host, 'service_port': port}
        for (name, host, port) in env_content
    ]
    dump_json_file(path=TARGET_FILE_PATH, content=config_file_content)


if __name__ == '__main__':
    create_db_content()
