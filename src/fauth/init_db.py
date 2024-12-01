#! /usr/bin/env python3

from .database import Base, engine
from .models import User


def init_db():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    print("Database tables created successfully!")
