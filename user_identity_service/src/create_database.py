import argparse
import logging

import sqlalchemy_utils

from .config import DB_CONN_STRING
from .app import app
from .model import db, User, persist_model_instance


logging.getLogger().setLevel(logging.INFO)


def create_database(root_user_name: str, root_password: str) -> None:
    if sqlalchemy_utils.database_exists(DB_CONN_STRING):
        logging.warning('Database already exists. Drop first if needed.')
        return None

    # create database structure
    app.app_context().push()
    sqlalchemy_utils.create_database(DB_CONN_STRING)
    db.create_all()

    # Create root user
    root = User(login=root_user_name, access_level=4)
    root.set_password(password=root_password)
    persist_model_instance(instance=root)

    logging.info(f'Root user created: {root.id}, {root.login}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser('Script to initialize database.')
    parser.add_argument(
        '--root_user_name',
        help='Main user login.',
        required=True
    )
    parser.add_argument(
        '--root_password',
        help='Main user password.',
        required=True
    )

    args = parser.parse_args()

    create_database(
        root_user_name=args.root_user_name,
        root_password=args.root_password
    )
