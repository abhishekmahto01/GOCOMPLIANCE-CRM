"""Core security module for password hashing, validation, and JWT handling."""
import hashlib
import re
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Tuple

import jwt
from pwdlib import PasswordHash

from app.core.config import settings

# Password hashing service utilizing Argon2id as recommended by pwdlib
password_hash_service = PasswordHash.recommended()

# Password complexity regex patterns
UPPERCASE_REGEX = re.compile(r"[A-Z]")
LOWERCASE_REGEX = re.compile(r"[a-z]")
DIGIT_REGEX = re.compile(r"[0-9]")
SPECIAL_CHAR_REGEX = re.compile(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?~`]")


def hash_password(password: str) -> str:
    """Hash a plaintext password using Argon2id.

    Args:
        password: Plaintext password string.

    Returns:
        Argon2id password hash string.
    """
    return password_hash_service.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against an Argon2id hash in constant time.

    Args:
        plain_password: Provided plaintext password.
        hashed_password: Stored Argon2id password hash.

    Returns:
        True if the password matches, False otherwise.
    """
    try:
        return password_hash_service.verify(plain_password, hashed_password)
    except Exception:
        return False


def validate_password_strength(password: str) -> None:
    """Validate password complexity against corporate security policies.

    Policy Rules:
    - Minimum 10 characters
    - Maximum 128 characters
    - At least one uppercase character [A-Z]
    - At least one lowercase character [a-z]
    - At least one digit [0-9]
    - At least one special symbol
    - Reject leading or trailing whitespace

    Args:
        password: The plaintext password to evaluate.

    Raises:
        ValueError: If any complexity requirement is violated.
    """
    if not isinstance(password, str):
        raise ValueError("Password must be a string")

    if password != password.strip():
        raise ValueError("Password cannot contain leading or trailing whitespace")

    if len(password) < 10:
        raise ValueError("Password must be at least 10 characters long")

    if len(password) > 128:
        raise ValueError("Password cannot exceed 128 characters")

    if not UPPERCASE_REGEX.search(password):
        raise ValueError("Password must contain at least one uppercase letter (A-Z)")

    if not LOWERCASE_REGEX.search(password):
        raise ValueError("Password must contain at least one lowercase letter (a-z)")

    if not DIGIT_REGEX.search(password):
        raise ValueError("Password must contain at least one digit (0-9)")

    if not SPECIAL_CHAR_REGEX.search(password):
        raise ValueError(
            "Password must contain at least one special character (!@#$%^&*...)"
        )


def hash_refresh_token(token: str) -> str:
    """Compute cryptographic SHA-256 hash of a raw refresh token for safe storage.

    Raw refresh tokens are never persisted in the database; only their cryptographic
    SHA-256 hash is stored.

    Args:
        token: Raw refresh token string.

    Returns:
        Hex-encoded SHA-256 hash string.
    """
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_access_token(
    user_id: uuid.UUID,
    token_version: int,
    expires_delta: Optional[timedelta] = None,
    jti: Optional[str] = None,
) -> str:
    """Create a signed JWT access token.

    Args:
        user_id: Unique identifier of the user (sub claim).
        token_version: Current token version for revocation tracking.
        expires_delta: Optional custom token expiration delta.
        jti: Optional unique JWT ID.

    Returns:
        Encoded JWT string.
    """
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload: Dict[str, Any] = {
        "sub": str(user_id),
        "type": "access",
        "token_version": token_version,
        "jti": jti or secrets.token_hex(16),
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def create_refresh_token(
    user_id: uuid.UUID,
    token_version: int,
    expires_delta: Optional[timedelta] = None,
    jti: Optional[str] = None,
) -> Tuple[str, str, datetime]:
    """Create a signed JWT refresh token.

    Args:
        user_id: Unique identifier of the user (sub claim).
        token_version: Current token version for revocation tracking.
        expires_delta: Optional custom expiration delta.
        jti: Optional unique JWT ID.

    Returns:
        Tuple containing:
        - raw_token: Signed raw JWT refresh token string
        - jti: Unique identifier string for database tracking
        - expires_at: Expiration datetime (timezone-aware UTC)
    """
    now = datetime.now(timezone.utc)
    if expires_delta:
        expires_at = now + expires_delta
    else:
        expires_at = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    token_jti = jti or secrets.token_hex(32)

    payload: Dict[str, Any] = {
        "sub": str(user_id),
        "type": "refresh",
        "token_version": token_version,
        "jti": token_jti,
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
    }

    raw_token = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    return raw_token, token_jti, expires_at


def decode_and_validate_token(
    token: str,
    expected_type: str = "access",
) -> Dict[str, Any]:
    """Decode and validate a JWT token's signature, expiry, and claims.

    Args:
        token: Raw encoded JWT string.
        expected_type: Expected 'type' claim ('access' or 'refresh').

    Returns:
        Decoded token payload dict.

    Raises:
        jwt.PyJWTError: If signature is invalid, expired, or claims are malformed.
        ValueError: If token type or required claims do not match expectations.
    """
    payload = jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
        options={"require": ["exp", "iat", "sub", "jti", "type"]},
    )

    if payload.get("type") != expected_type:
        raise ValueError(
            f"Invalid token type: expected '{expected_type}', got '{payload.get('type')}'"
        )

    if "token_version" not in payload:
        raise ValueError("Token is missing required 'token_version' claim")

    return payload
