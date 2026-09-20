"""Refresh Token model definition."""
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class RefreshToken(Base):
    """Store hashed rotating refresh tokens for authenticated sessions."""

    __tablename__ = "auth_refresh_token"
    __table_args__ = (
        {"comment": "Registry for hashed rotating refresh tokens and session revocation"},
    )

    refresh_token_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Unique identifier for the refresh token record (UUIDv4)",
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "user_master.user_id",
            ondelete="CASCADE",
            name="fk_refresh_token_user_id",
        ),
        nullable=False,
        index=True,
        comment="Foreign key referencing user_master.user_id (ON DELETE CASCADE)",
    )

    jti: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique JWT identifier (JTI) of the refresh token",
    )

    token_hash: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        index=True,
        comment="Cryptographic SHA-256 hash of the issued refresh token (raw token is never stored)",
    )

    issued_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Timestamp when the refresh token was issued (UTC)",
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="Expiration timestamp for the refresh token (UTC)",
    )

    revoked_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        comment="Timestamp when the token was explicitly revoked/logged out/rotated (UTC)",
    )

    replaced_by_jti: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
        comment="JTI of the replacement refresh token upon rotation (for reuse detection)",
    )

    created_ip: Mapped[Optional[str]] = mapped_column(
        String(45),
        nullable=True,
        comment="Client IP address that requested the token",
    )

    user_agent: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Client user agent string",
    )

    # ORM Relationship to User
    user: Mapped["User"] = relationship(
        "User",
        back_populates="refresh_tokens",
    )

    def __repr__(self) -> str:
        return (
            f"<RefreshToken(id='{self.refresh_token_id}', "
            f"user_id='{self.user_id}', "
            f"jti='{self.jti}', "
            f"revoked={self.revoked_at is not None})>"
        )
