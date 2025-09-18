from flask import Flask
from flask_restx import Api

from .database import db
from flask_jwt_extended import JWTManager
from .auth import ns as auth_ns
from .products import ns as products_ns
from .cart import ns as cart_ns


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY="dev-secret",
        SQLALCHEMY_DATABASE_URI="sqlite:///ecom.db",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        JWT_SECRET_KEY="jwt-secret",
        PROPAGATE_EXCEPTIONS=True,
        RESTX_MASK_SWAGGER=False,
    )
    if test_config:
        app.config.update(test_config)
    db.init_app(app)
    JWTManager(app)
    api = Api(
        app,
        version="1.0.0",
        title="E-commerce API",
        description="Flask + SQLite + JWT. Auto-documented with flask-restx.",
        doc="/docs",
    )

    api.add_namespace(auth_ns, path="/auth")
    api.add_namespace(products_ns, path="/products")
    api.add_namespace(cart_ns, path="/cart")

    with app.app_context():
        db.create_all()
    return app
