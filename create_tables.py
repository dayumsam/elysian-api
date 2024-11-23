# Adjust the import path as necessary
from models import Styles, Suggestion, Images, Contact
import os
from sqlmodel import SQLModel, create_engine
from dotenv import load_dotenv

load_dotenv()


DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')

if not DATABASE_URI:
    raise ValueError(
        "The SQLALCHEMY_DATABASE_URI environment variable is not set.")

engine = create_engine(DATABASE_URI)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    print("Tables created successfully.")


if __name__ == "__main__":
    create_db_and_tables()
