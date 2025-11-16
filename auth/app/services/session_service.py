import uuid
from datetime import datetime

from sqlalchemy.orm import Session
from app.models import Session as UserSession


def create_session(
    db: Session,
    user_id: str,
    device_id: uuid.UUID,
    user_agent: str,
    ip: str,
    refresh_token_hash: str,
    expires_at: datetime
) -> UserSession:
    session = UserSession(
        id=uuid.uuid4(),
        user_id=user_id,
        device_id=device_id,
        user_agent=user_agent,
        ip=ip,
        refresh_token_hash=refresh_token_hash,
        expires_at=expires_at,
        revoked_at=None,
        created_at=datetime.utcnow()
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def revoke_session(db: Session, user_id: uuid.UUID):
    session = db.query(UserSession).filter(
        UserSession.user_id == user_id,
        UserSession.revoked_at.is_(None)
    ).first()

    if session and not session.revoked_at:
        session.revoked_at = datetime.utcnow()
        db.commit()


def revoke_all_sessions_for_user(db: Session, user_id: uuid.UUID):
    db.query(UserSession).filter(
        UserSession.user_id == user_id,
        UserSession.revoked_at.is_(None)
    ).update({UserSession.revoked_at: datetime.utcnow()})

    db.commit()
