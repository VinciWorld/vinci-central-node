from decouple import config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.configuration.settings import settings

engine = create_engine(str(settings.db_url), pool_pre_ping=True)
Session = sessionmaker(bind=engine)


def get_db_session():
    try:
        db_session = Session()
        yield db_session
    finally:
        db_session.rollback()
        db_session.close()