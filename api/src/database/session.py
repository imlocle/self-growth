from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


BASE = declarative_base()


def get_db_engine(conn_str: str, debug=False):
    engine = create_engine(conn_str, echo=debug)
    return engine


def get_db_session(conn_str: str, debug=False):
    sessmaker = sessionmaker(bind=get_db_engine(conn_str, debug))
    session = sessmaker()
    return session


# These imports are down here to prevent cyclic imports
# they are not used in this file but are required for
# alembic to include tables in revision generation.
from src.models.to_do import ToDoTable  # noqa: E402,F401
from src.models.habit import HabitTable, HabitEventsTable  # noqa: E402,F401
