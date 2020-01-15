from typing import Optional, List

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def persist_model_instance(instance: db.Model) -> None:
    db.session.add(instance)
    commit_db_changes()


def remove_from_db(instance: db.Model) -> None:
    db.session.delete(instance)
    commit_db_changes()


def commit_db_changes() -> None:
    db.session.commit()


class ServiceLocation(db.Model):
    __tablename__ = 'services_discovery_data'
    __table_args__ = (
        db.CheckConstraint('service_port > 0 and service_port < 65536'),
    )

    id = db.Column(db.Integer, primary_key=True)
    service_name = db.Column(db.String(128), unique=True, nullable=False)
    service_address = db.Column(db.String(256), nullable=False)
    service_port = db.Column(db.Integer, nullable=False)

    @classmethod
    def find_by_name(cls, service_name: str) -> Optional['ServiceLocation']:
        return cls.query.filter_by(service_name=service_name).first()

    @classmethod
    def get_all(cls) -> List['ServiceLocation']:
        return cls.query.all()
