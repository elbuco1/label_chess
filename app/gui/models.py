from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, \
    ForeignKey, Table

import shutil
import os

DB_PATH = "sqlite:///db.sqlite"
ENGINE = create_engine(url=DB_PATH)
SESSION = sessionmaker(bind=ENGINE)
BASE = declarative_base(bind=ENGINE)
DB_DATA_DIR = "database"
VIDEO_DATA_DIR = os.path.join(DB_DATA_DIR, "video")
PGN_DATA_DIR = os.path.join(DB_DATA_DIR, "pgn")
ANNOTATIONS_DATA_DIR = os.path.join(DB_DATA_DIR, "annotations")


def init_db(clear=False):
    """Create database, and data
    directory.

    If clear is True, database is reset
    and data directory is emptied.
    """
    if clear:
        BASE.metadata.drop_all()
        if os.path.exists(DB_DATA_DIR):
            shutil.rmtree(DB_DATA_DIR)

    os.makedirs(VIDEO_DATA_DIR, exist_ok=True)
    os.makedirs(PGN_DATA_DIR, exist_ok=True)
    os.makedirs(ANNOTATIONS_DATA_DIR, exist_ok=True)

    BASE.metadata.create_all(checkfirst=True)


def get_db():
    """Get a database session.
    """
    db = SESSION()
    return db


def todict(obj):
    """ Return the object's dict excluding private attributes, 
    sqlalchemy state and relationship attributes.
    """
    excl = ('_sa_adapter', '_sa_instance_state')
    return {k: v for k, v in vars(obj).items() if not k.startswith('_') and
            not any(hasattr(v, a) for a in excl)}


class Repr_MIXIN():
    """Enable print of a model instance.
    """

    def __repr__(self):
        params = ', '.join(f'{k}={v}' for k, v in todict(self).items())
        return f"{self.__class__.__name__}({params})"


class Video(BASE, Repr_MIXIN):
    __tablename__ = "video"
    # video url used as primary key as it should
    # be unique
    url = Column(String, primary_key=True)
    # path from where the video is loaded
    original_path = Column(String)
    # path where the video is copied
    path = Column(String)
    # title of the video
    name = Column(String, unique=True)


class PGN(BASE, Repr_MIXIN):
    __tablename__ = "pgn"
    # pgn url used as primary key as it should
    # be unique
    url = Column(String, primary_key=True)
    # path to the pgn on disk
    path = Column(String)
    # path from where the pgn file is loaded
    original_path = Column(String)
    # name of the game
    name = Column(String, unique=True)


class Annotation(BASE, Repr_MIXIN):
    __tablename__ = "annotation"
    # pgn url used as primary key as it should
    # be unique
    id = Column(Integer, primary_key=True, autoincrement=True)
    # corresponding video
    video_url = Column(String, ForeignKey('video.url'))
    # corresponding pgn
    pgn_url = Column(String, ForeignKey('pgn.url'))
    # path to csv file containing moves
    csv_path = Column(String, unique=True)
