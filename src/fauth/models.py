from sqlmodel import Column, String
from .database import Base


class User(Base):
    __tablename__: str = "users"
    username: str = Column(
        String, primary_key=True, index=True, unique=True, nullable=False
    )
    email: str = Column(String, unique=True, nullable=False)
    hashed_password: str = Column(String, nullable=False)
    role: str = Column(String, default="user", nullable=False)  # user | superuser
