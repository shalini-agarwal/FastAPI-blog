from __future__ import annotations # for Python versions older than 3.14

from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    image_file: Mapped[str | None] = mapped_column( # this stores just the file name without the path; this de-couples the db from the file structure; this helps in organizing the file structure later on without affecting the strcuture in the db
        String(200),
        nullable=True,
        default=None,
    )

    ''' one to many relationship; one user can have many posts
        We are referencing the Post before it's being defined below; this is called as foward-referencing'''
    posts: Mapped[list[Post]] = relationship(back_populates="author", cascade='all, delete-orphan') # tells SQLAlchemy to delete all their posts when a user is deleted

    @property
    def image_path(self) -> str:
        if self.image_file:
            return f"/media/profile_pics/{self.image_file}" # this essentially separates the static files which is shipped with the app from the user uploaded profile photos
        return "/static/profile_pics/default.jpg"


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    date_posted: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), # SQLite stores datetime as text but this will ensure PostgreSQL will use timestamp TZ when we migrate later 
        default=lambda: datetime.now(UTC), # gets called by default when a post gets created to set the post creation time to the current time
    )

    author: Mapped[User] = relationship(back_populates="posts") # many to one relationship
