from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, \
    ForeignKey, Table

DB_PATH = "sqlite:///db.sqlite"
ENGINE = create_engine(url=DB_PATH)
SESSION = sessionmaker(bind=ENGINE)
BASE = declarative_base(bind=ENGINE)


def init_db(clear=False):
    """Remove every table in db and
    create all dbs.
    TODO initialization scheme of database (create tables)
    """
    if clear:
        BASE.metadata.drop_all()
    BASE.metadata.create_all(checkfirst=True)


def get_db():
    """Get a database session.
    """
    db = SESSION()
    return db


class Video(BASE):
    __tablename__ = "video"
    # video url used as primary key as it should
    # be unique
    url = Column(String, primary_key=True)
    # path to the video on disk
    path = Column(String)
