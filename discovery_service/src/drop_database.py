import logging

import sqlalchemy_utils
from sqlalchemy_utils import drop_database

from .config import DB_CONN_STRING

logging.getLogger().setLevel(logging.INFO)


def drop_db() -> None:
    if sqlalchemy_utils.database_exists(DB_CONN_STRING):
        drop_database(DB_CONN_STRING)
        logging.info('Services location database deleted')
    else:
        logging.info("Database does not exist.")


if __name__ == '__main__':
    drop_db()
