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
    # path to the video on disk
    path = Column(String)


class PGN(BASE, Repr_MIXIN):
    __tablename__ = "pgn"
    # pgn url used as primary key as it should
    # be unique
    url = Column(String, primary_key=True)
    # path to the pgn on disk
    path = Column(String)
