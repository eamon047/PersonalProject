from datetime import timedelta
from app.security import get_password_hash, verify_password, create_access_token, verify_token

def test_password_hash_and_verify():
    pw = "S3cret!"
    h = get_password_hash(pw)
    assert h != pw
    assert verify_password(pw, h) is True
    assert verify_password("wrong", h) is False

def test_jwt_create_and_verify_ok():
    token = create_access_token({"sub": "123"}, expires_delta=timedelta(minutes=5))
    assert verify_token(token) == "123"

def test_jwt_expired_is_invalid():
    token = create_access_token({"sub": "123"}, expires_delta=timedelta(seconds=-1))  # 立刻过期
    assert verify_token(token) is None
