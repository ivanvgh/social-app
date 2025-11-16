import uuid

from sqlalchemy.orm.session import Session

from app.models import User
from app.schemas import RegisterRequest
from app.security import hash_password


def create_user(db: Session, payload: RegisterRequest) -> User:
    user = User(
        id=uuid.uuid4(),
        username=payload.username,
        email=payload.email,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter_by(email=email).first()
