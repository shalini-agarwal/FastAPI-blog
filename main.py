from fastapi import FastAPI, Request, HTTPException, status, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from typing import Annotated

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import models
from database import Base, engine, get_db

from contextlib import asynccontextmanager
from fastapi.exception_handlers import http_exception_handler, request_validation_exception_handler

from routers import posts, users

from config import settings

# create_all is synchronous. We can't call synchronous methods with async engine. We need to remove this line and instead create our tables in a lifespan function.
# lifespan is a modern way in FastAPI to handle start-up and shutdown events. It replaces the older deprecated on-startup and on-shutdown decorators.
# Base.metadata.create_all(bind=engine) 


# Asynchronous way of creating the db tables. If they do exist then, because it is idempotent, it can be run multiple times and it won't have any side effects.?
@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.mount("/media", StaticFiles(directory="media"), name="media")

templates = Jinja2Templates(directory="templates")

app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(posts.router, prefix="/api/posts", tags=["posts"])
# tag parameter organizes the /docs page. It creates collapsables sections. All the users endpoints will appear under a users header and similar for posts.

@app.get("/", include_in_schema=False, name="home")
@app.get("/posts", include_in_schema=False, name="posts")
async def home(request: Request, db: Annotated[AsyncSession, Depends(get_db)]):
    count_result = await db.execute(select(func.count()).select_from(models.Post))
    total = count_result.scalar() or 0

    result = await db.execute(
        select(models.Post)
        .options(selectinload(models.Post.author))
        .order_by(models.Post.date_posted.desc())
        .limit(settings.posts_per_page),
    ) # there is not offset (i.e. skip) here as compared to the api as it will always be the first page
    
    posts = result.scalars().all()

    has_more = len(posts) < total

    '''
    This is going to be a hybrid approach here as the first batch is going to be server side rendered so that the page loads fast and search engine can see the content.
    The subsequent batches are going to be fetched by JavaScript. So it is going to be fast initial load and then some dynamic loading after that.
    '''
    return templates.TemplateResponse(
        request,
        "home.html",
        {
            "posts": posts,
            "title": "Home",
            "limit": settings.posts_per_page,
            "has_more": has_more,
        }, 
    )
# same pagination logic as in the api but this time we're only getting the first batch for server side rendering 

@app.get("/posts/{post_id}", include_in_schema=False)
async def post_page(request: Request, post_id: int, db: Annotated[AsyncSession, Depends(get_db)]): # using type hinting helps FastAPI to automatically validate the input
    result = await db.execute(select(models.Post).options(selectinload(models.Post.author)).where(models.Post.id == post_id))
    post = result.scalars().first()
    if post:
        title = post.title[:50]
        return templates.TemplateResponse(
            request, 
            "post.html", 
            {"post": post, "title": title})

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

@app.get("/users/{user_id}/posts", include_in_schema=False, name="user_posts")
async def user_posts_page(
    request: Request,
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    count_result = await db.execute(
        select(func.count())
        .select_from(models.Post)
        .where(models.Post.user_id == user_id),
    )
    total = count_result.scalar() or 0

    result = await db.execute(
        select(models.Post)
        .options(selectinload(models.Post.author))
        .where(models.Post.user_id == user_id)
        .order_by(models.Post.date_posted.desc())
        .limit(settings.posts_per_page),
    )
    posts = result.scalars().all()

    has_more = len(posts) < total

    return templates.TemplateResponse(
        request,
        "user_posts.html",
        {
            "posts": posts,
            "user": user,
            "title": f"{user.username}'s Posts",
            "limit": settings.posts_per_page,
            "has_more": has_more,
        },
    )

@app.get("/login", include_in_schema=False)
async def login_page(request: Request):
    return templates.TemplateResponse(
        request,
        "login.html",
        {"title": "Login"},
    )


@app.get("/register", include_in_schema=False)
async def register_page(request: Request):
    return templates.TemplateResponse(
        request,
        "register.html",
        {"title": "Register"},
    )

# account page for the user where the user can see their account info
'''We are not protecting this endpoint on the server like we are protecting the api endpoints because our token is stored in local storage which is only accessible by JS running in the browser.
So when someone navigates to /account, the browser makes a regular GET request, it doesn't automatically include the token from local storage. 
So the server has no way to know if you are logged in when it renders the page. 
Instead we handle this with JS on the front end. So when the page loads, our JS checks if you're logged in and refirects you to the login page if you're not.
This is just a user experience convenience. It prevents non-logged users from seeing a broken page. 
But it is not real security. Someone could technically view this HTML page if they wanted to by disabling JS. But the actual security comes from the API endpoints.
Any attempt to update or delete any account will fail with a 401 error because the API requires a valid token. 
It is nice to reply on the front-end for user experience type of thing but it is always on our backend to handle the security.
'''
@app.get("/account", include_in_schema=False)
async def account_page(request: Request):
    return templates.TemplateResponse(
        request,
        "account.html",
        {"title": "Account"},
    )


@app.exception_handler(StarletteHTTPException)
async def general_http_exception_handler(request: Request, exception: StarletteHTTPException):

    if request.url.path.startswith("/api"):
        return await http_exception_handler(request, exception)

    message = (
    exception.detail
    if exception.detail
    else "An error occurred. Please check your request and try again.")

    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": exception.status_code,
            "title": exception.status_code,
            "message": message,
        },
        status_code=exception.status_code, # this line makes sure to tell the browser the correct HTTP status response code
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exception: RequestValidationError):
    if request.url.path.startswith("/api"):
        return await request_validation_exception_handler(request, exception)

    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "title": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "message": "Invalid request. Please check your input and try again.",
        },
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
    )