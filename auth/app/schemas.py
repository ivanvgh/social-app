from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, StringConstraints


Str50 = Annotated[str, StringConstraints(min_length=3, max_length=50)]
Pwd6 = Annotated[str, StringConstraints(min_length=6)]


class RegisterRequest(BaseModel):
    username: Str50
    email: EmailStr
    password: Pwd6


class RegisterResponse(BaseModel):
    id: UUID
    username: str
    email: EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: Literal['bearer'] = 'bearer'
    user_id: UUID
    expires_at: datetime


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    username: str
    email: EmailStr


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str


class RefreshRequest(BaseModel):
    refresh_token: str
