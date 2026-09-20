"""Unit tests for core security, password hashing, and JWT token management."""
import time
import uuid
from datetime import timedelta

import jwt
import pytest

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_and_validate_token,
    hash_password,
    hash_refresh_token,
    validate_password_strength,
    verify_password,
)


def test_password_hashing_and_verification() -> None:
    """Verify that password hashing uses Argon2id and verifies correctly."""
    plain_pw = "SecurePass123!@"
    hashed = hash_password(plain_pw)

    assert hashed.startswith("$argon2id$")
    assert hashed != plain_pw
    assert verify_password(plain_pw, hashed) is True
    assert verify_password("WrongPassword123!", hashed) is False
    assert verify_password("", hashed) is False


def test_password_strength_valid() -> None:
    """Verify strong passwords pass validation without errors."""
    valid_passwords = [
        "GoCompliance2026!#",
        "Admin_Passw0rd",
        "Str0ng&Complex!123",
        "P@ssw0rdForAdmin$",
    ]
    for pw in valid_passwords:
        validate_password_strength(pw)  # Should not raise


def test_password_strength_invalid_cases() -> None:
    """Verify weak or malformed passwords raise ValueError with descriptive details."""
    # Too short (< 10 chars)
    with pytest.raises(ValueError) as exc_info:
        validate_password_strength("Short1!")
    assert "at least 10 characters long" in str(exc_info.value)

    # Missing uppercase
    with pytest.raises(ValueError) as exc_info:
        validate_password_strength("lowercase123!@#")
    assert "uppercase letter" in str(exc_info.value)

    # Missing lowercase
    with pytest.raises(ValueError) as exc_info:
        validate_password_strength("UPPERCASE123!@#")
    assert "lowercase letter" in str(exc_info.value)

    # Missing digit
    with pytest.raises(ValueError) as exc_info:
        validate_password_strength("NoDigitsHere!@#")
    assert "digit" in str(exc_info.value)

    # Missing special symbol
    with pytest.raises(ValueError) as exc_info:
        validate_password_strength("NoSpecialChar12345")
    assert "special character" in str(exc_info.value)

    # Leading/trailing whitespace
    with pytest.raises(ValueError) as exc_info:
        validate_password_strength("  LeadingSpace123!  ")
    assert "leading or trailing whitespace" in str(exc_info.value)

    # Exceeding 128 characters
    with pytest.raises(ValueError) as exc_info:
        validate_password_strength("A" * 125 + "a1!" + "B" * 10)
    assert "cannot exceed 128 characters" in str(exc_info.value)


def test_hash_refresh_token_sha256() -> None:
    """Verify refresh token SHA-256 hashing produces deterministic non-raw hashes."""
    raw_token = "some_random_jwt_refresh_token_string"
    hashed_1 = hash_refresh_token(raw_token)
    hashed_2 = hash_refresh_token(raw_token)

    assert hashed_1 == hashed_2
    assert len(hashed_1) == 64  # Hex-encoded SHA-256 is 64 chars
    assert hashed_1 != raw_token


def test_access_token_creation_and_claims() -> None:
    """Verify access token contains sub, type='access', token_version, and valid expiry."""
    user_id = uuid.uuid4()
    token_version = 2
    token = create_access_token(user_id=user_id, token_version=token_version)

    payload = decode_and_validate_token(token, expected_type="access")
    assert payload["sub"] == str(user_id)
    assert payload["type"] == "access"
    assert payload["token_version"] == 2
    assert "jti" in payload
    assert payload["exp"] > payload["iat"]


def test_refresh_token_creation_and_claims() -> None:
    """Verify refresh token contains sub, type='refresh', unique JTI, and valid expiry."""
    user_id = uuid.uuid4()
    token_version = 1
    raw_token, jti, expires_at = create_refresh_token(
        user_id=user_id,
        token_version=token_version,
    )

    payload = decode_and_validate_token(raw_token, expected_type="refresh")
    assert payload["sub"] == str(user_id)
    assert payload["type"] == "refresh"
    assert payload["jti"] == jti
    assert payload["token_version"] == 1
    assert expires_at is not None


def test_token_type_mismatch_rejection() -> None:
    """Verify access token cannot be used where a refresh token is expected and vice-versa."""
    user_id = uuid.uuid4()
    access_token = create_access_token(user_id=user_id, token_version=1)
    raw_refresh, _, _ = create_refresh_token(user_id=user_id, token_version=1)

    with pytest.raises(ValueError) as exc_info:
        decode_and_validate_token(access_token, expected_type="refresh")
    assert "Invalid token type: expected 'refresh'" in str(exc_info.value)

    with pytest.raises(ValueError) as exc_info:
        decode_and_validate_token(raw_refresh, expected_type="access")
    assert "Invalid token type: expected 'access'" in str(exc_info.value)


def test_expired_token_rejection() -> None:
    """Verify expired token raises jwt.ExpiredSignatureError."""
    user_id = uuid.uuid4()
    expired_token = create_access_token(
        user_id=user_id,
        token_version=1,
        expires_delta=timedelta(seconds=-10),
    )

    with pytest.raises(jwt.ExpiredSignatureError):
        decode_and_validate_token(expired_token, expected_type="access")


def test_tampered_signature_rejection() -> None:
    """Verify token signed with different secret is rejected."""
    user_id = uuid.uuid4()
    fake_token = jwt.encode(
        {
            "sub": str(user_id),
            "type": "access",
            "token_version": 1,
            "jti": "fake",
            "iat": int(time.time()),
            "exp": int(time.time() + 600),
        },
        "wrong_secret_key_123456789012345678901234567890",
        algorithm="HS256",
    )

    with pytest.raises(jwt.InvalidSignatureError):
        decode_and_validate_token(fake_token, expected_type="access")
