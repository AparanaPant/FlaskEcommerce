from app.models import User

def test_user_password_hash_and_check():
    u = User(email="unit@test.com")
    u.set_password("secret123")
    assert u.password_hash != "secret123"
    assert u.check_password("secret123") is True
    assert u.check_password("wrong") is False
