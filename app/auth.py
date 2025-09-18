from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_access_token
from .database import db
from .models import User

ns = Namespace("auth", description="User registration & login")

login_model = ns.model("Login", {
    "email": fields.String(required=True, example="a@b.com"),
    "password": fields.String(required=True, example="secret"),
})

register_model = ns.clone("Register", login_model)

token_model = ns.model("TokenResponse", {
    "access_token": fields.String(example="<JWT>"),
})

message_model = ns.model("RegisterResponse", {
    "message": fields.String(example="registered"),
    "user_id": fields.Integer(example=1),
})

@ns.route("/register")
class Register(Resource):
    @ns.expect(register_model, validate=True)
    @ns.response(201, "Created", message_model)
    @ns.response(400, "Missing fields")
    @ns.response(409, "Email already registered")
    def post(self):
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")
        if not email or not password:
            ns.abort(400, "email and password required")
        if User.query.filter_by(email=email).first():
            ns.abort(409, "email already registered")

        user = User(email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return {"message": "registered", "user_id": user.id}, 201

@ns.route("/login")
class Login(Resource):
    @ns.expect(login_model, validate=True)
    @ns.response(200, "OK", token_model)
    @ns.response(401, "Invalid credentials")
    def post(self):
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            ns.abort(401, "invalid credentials")
        token = create_access_token(identity=user.id)
        return {"access_token": token}
