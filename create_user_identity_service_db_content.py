import os

from config_generation_utils import dump_json_file, fetch_from_env

TARGET_FILE_PATH = os.path.join("./user_identity_service/db_content.json")

TO_FETCH_FROM_ENV = [
    ('ROOT_USER_NAME', 'ROOT_PASSWORD'),
]


def create_db_content() -> None:
    env_content = fetch_from_env(to_fetch=TO_FETCH_FROM_ENV)
    config_file_content = {
        'login': env_content[0][0], 'password': env_content[0][1]
    }
    dump_json_file(path=TARGET_FILE_PATH, content=config_file_content)


if __name__ == '__main__':
    create_db_content()
