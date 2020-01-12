import logging

from .app import app
from .model import db

logging.getLogger().setLevel(logging.INFO)


def drop_database() -> None:
    app.app_context().push()
    db.drop_all()
    logging.info("Database dropped")


if __name__ == '__main__':
    drop_database()
