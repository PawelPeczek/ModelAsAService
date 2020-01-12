import logging

import sqlalchemy_utils

from .config import DB_CONN_STRING
from .app import app
from .model import db


logging.getLogger().setLevel(logging.INFO)


def create_database() -> None:
    if not sqlalchemy_utils.database_exists(DB_CONN_STRING):
        app.app_context().push()
        sqlalchemy_utils.create_database(DB_CONN_STRING)
        db.create_all()
        logging.info(f'Services identity database created')
    else:
        logging.warning('Database already exists. Drop first if needed.')


if __name__ == '__main__':
    create_database()

