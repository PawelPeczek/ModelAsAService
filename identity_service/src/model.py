from typing import Optional

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


def persist_model_instance(instance: db.Model) -> None:
    db.session.add(instance)
    commit_db_changes()


def commit_db_changes() -> None:
    db.session.commit()


def remove_from_db(instance: db.Model) -> None:
    db.session.delete(instance)
    db.session.commit()


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(128), unique=True, nullable=False)
    password = db.Column(db.String(256), unique=False, nullable=False)
    access_level = db.Column(db.Integer, nullable=False, default=1)

    @classmethod
    def find_by_credentials(cls, login: str, password: str) -> Optional['User']:
        matching_user = cls.find_by_login(login=login)
        if matching_user is None:
            return None
        if matching_user.check_password(password=password):
            return matching_user
        else:
            return None

    @classmethod
    def find_by_login(cls, login: str) -> Optional['User']:
        return cls.query.filter_by(login=login).first()

    def set_password(self, password: str) -> None:
        self.password = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)
