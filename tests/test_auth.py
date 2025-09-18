import jwt
from flask import current_app


def register(client, email="a@b.com", password="secret"):
    return client.post("/auth/register", json={"email": email, "password": password})


def login(client, email="a@b.com", password="secret"):
    return client.post("/auth/login", json={"email": email, "password": password})


def test_register_and_login_flow(client):
    r = register(client)
    assert r.status_code == 201

    r = login(client)
    assert r.status_code == 200
    token = r.get_json()["access_token"]
    assert token

    # Basic token shape
    header = jwt.get_unverified_header(token)
    assert header["alg"] in {"HS256", "RS256"}