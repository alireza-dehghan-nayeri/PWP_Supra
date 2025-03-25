# tests/conftest.py

import os
import tempfile
import pytest
from food_manager import create_app, db
from sqlalchemy.engine import Engine
from sqlalchemy import event

@event.listens_for(Engine, "connect")
def enable_sqlite_foreign_keys(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

@pytest.fixture()
def app():
    db_fd, db_path = tempfile.mkstemp()
    config = {
        "SQLALCHEMY_DATABASE_URI": "sqlite:///" + db_path,
        "TESTING": True
    }

    app = create_app(config)

    with app.app_context():
        db.create_all()
        yield app

        db.session.remove()
        db.drop_all()

    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture()
def client(app):
    yield app.test_client()

    with app.app_context():
        db.session.remove()
        db.drop_all()

@pytest.fixture()
def session(app):
    with app.app_context():
        yield db.session

        db.session.remove()
        db.drop_all()
