import json
import os

if __name__ == '__main__':
    with open('./db_content.json', mode='r') as f:
        root_user_specs = json.load(f)
    os.system('python -m src.drop_database')
    os.system(
        'python -m src.create_database '
        f'--root_user_name={root_user_specs["login"]} '
        f'--root_password={root_user_specs["password"]}'
    )
