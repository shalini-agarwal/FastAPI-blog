from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./blog.db"

engine = create_engine( # this is the connection to the database
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}, # SQLite allows only one thread but FastAPI handles multiple requests across threads hence we disable this configuration for SQLite
)

'''A factory that creates database sessions; session is a transaction with the db; each request gets its own session.
    autocommit and autoflush is turned false because we want to control when the change happens.'''
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) 

class Base(DeclarativeBase):
    pass

''' Dependency function that provides session to the routes; it is generator using yield; the with statement makes the session work as a context manager similar to opening a file; this ensures clean up when an error occurs.
    FastAPI's dependency injection calls this function for each request and handles that clean-up automatically.
    Dependency injection is basically a way of saying - 'this route needs a db session to work so go ahead and provide one'. Instead of creating a session inside the route, we declare that we need one and FastAPI provides one.  '''
def get_db():
    with SessionLocal() as db:
        yield db
