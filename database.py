from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./blog.db" # this tells SQLAlchemy which async driver to use for SQLite db

engine = create_async_engine( # this is the connection to the database
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}, # SQLite allows only one thread but FastAPI handles multiple requests across threads hence we disable this configuration for SQLite
)

'''A factory that creates database sessions; session is a transaction with the db; each request gets its own session.
    autocommit and autoflush is turned false because we want to control when the change happens.'''
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False # recommended for async, prevents issues with expired objects after a commit. When an object expires, SQLAlchemy tries to reload it lazily but lazy loading doesn't work in async.
) 

class Base(DeclarativeBase):
    pass

''' Dependency function that provides session to the routes; it is generator using yield; the with statement makes the session work as a context manager similar to opening a file; this ensures clean up when an error occurs.
    FastAPI's dependency injection calls this function for each request and handles that clean-up automatically.
    Dependency injection is basically a way of saying - 'this route needs a db session to work so go ahead and provide one'. Instead of creating a session inside the route, we declare that we need one and FastAPI provides one.  '''
async def get_db():
    async with AsyncSessionLocal() as session: # it is still a generator that yields a session but now it is an async generator
        yield session
