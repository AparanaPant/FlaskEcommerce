import os, tempfile, pytest
from app import create_app
from app.database import db

@pytest.fixture()
def app():
    db_fd, db_path = tempfile.mkstemp()
    test_app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
        "JWT_SECRET_KEY": "test-jwt",
        "SECRET_KEY": "test-secret",
    })
    with test_app.app_context():
        db.create_all()
    try:
        yield test_app
    finally:
        with test_app.app_context():
            db.session.remove()
            db.engine.dispose()
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture() 
def client(app):
    return app.test_client()

