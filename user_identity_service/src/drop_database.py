import logging

import sqlalchemy_utils

from .config import DB_CONN_STRING

logging.getLogger().setLevel(logging.INFO)


def drop_database() -> None:
    if sqlalchemy_utils.database_exists(DB_CONN_STRING):
        sqlalchemy_utils.drop_database(DB_CONN_STRING)
        logging.info('User identity database deleted')
    else:
        logging.info("Database does not exist.")


if __name__ == '__main__':
    drop_database()
