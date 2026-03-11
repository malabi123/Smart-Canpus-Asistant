from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
from dotenv import load_dotenv
from os import getenv
from contextlib import contextmanager

load_dotenv()

DATABASE_URL = getenv('DATABASE_URL')

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found")

Base = declarative_base()
engine = create_engine(DATABASE_URL)
local_session = sessionmaker(bind=engine)


@contextmanager
def get_session():
    Base.metadata.create_all(engine)
    session = local_session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
