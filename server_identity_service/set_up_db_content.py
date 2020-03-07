import os

if __name__ == '__main__':
    os.system('python -m src.drop_database')
    os.system('python -m src.create_database')
    os.system('python -m src.manage_services --config_path="./db_content.json"')
