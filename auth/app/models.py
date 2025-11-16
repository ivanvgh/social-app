# auth/app/models.py
import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, DateTime,
    ForeignKey, UniqueConstraint, Index
)
from sqlalchemy.dialects.postgresql import UUID, INET
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    __table_args__ = (
        Index('ix_users_username', 'username'),
        Index('ix_users_email', 'email'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(120), nullable=False, unique=True)
    password_hash = Column(Text, nullable=False)
    avatar_url = Column(Text)
    bio = Column(Text)
    email_verified_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Session(Base):
    __tablename__ = 'sessions'
    __table_args__ = (
        UniqueConstraint('user_id', 'device_id', name='uq_user_device'),
        Index('ix_sessions_expires_at', 'expires_at'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    device_id = Column(UUID(as_uuid=True), nullable=False)
    user_agent = Column(Text, nullable=False)
    ip = Column(INET, nullable=False)
    refresh_token_hash = Column(Text, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    revoked_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
