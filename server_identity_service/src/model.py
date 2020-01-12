from typing import Optional, List

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


def persist_model_instance(instance: db.Model) -> None:
    db.session.add(instance)
    commit_db_changes()


def remove_from_db(instance: db.Model) -> None:
    db.session.delete(instance)
    commit_db_changes()


def commit_db_changes() -> None:
    db.session.commit()


class Service(db.Model):
    __tablename__ = 'services'

    id = db.Column(db.Integer, primary_key=True)
    service_name = db.Column(db.String(128), unique=True, nullable=False)
    password = db.Column(db.String(256), unique=False, nullable=False)

    @classmethod
    def find_by_credentials(cls,
                            service_name: str,
                            password: str) -> Optional['Service']:
        service = Service.find_by_name(service_name=service_name)
        if service is None:
            return None
        if service.check_password(password=password):
            return service
        else:
            return None

    @classmethod
    def find_by_name(cls, service_name: str) -> Optional['Service']:
        return cls.query.filter_by(service_name=service_name).first()


    @classmethod
    def get_all(cls) -> List['Service']:
        return cls.query.all()

    def set_password(self, password: str) -> None:
        self.password = generate_password_hash(password=password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)
