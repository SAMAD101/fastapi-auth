from sqlmodel import create_engine, SQLModel, Session

from fastapi import Depends

from typing import Annotated


SQLALCHEMY_DATABASE_URL = "sqlite:///./fauth.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
