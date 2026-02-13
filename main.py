from fastapi import FastAPI, Request, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

posts: list[dict] = [
    {
        "id":1,
        "author": "Corey Schafer",
        "title": "Getting started with FastAPI",
        "content": "Very popular framework",
        "date_posted": "February 12,2026",
    },
    {
        "id":2,
        "author": "Jane Doe",
        "title": "Advance concepts in Python",
        "content": "Python is very user-friendly and quick to get started with!",
        "date_posted": "February 15,2026",
    },
]

@app.get("/", include_in_schema=False, name='home')
@app.get("/posts", include_in_schema=False, name='posts')
def home(request: Request):
    return templates.TemplateResponse(
        request, 
        "home.html", 
        {"posts": posts, "title": "Home"})

@app.get("/posts/{post_id}", include_in_schema=False)
def post_page(request: Request, post_id: int): # using type hinting helps FastAPI to automatically validate the input
    for post in posts:
        if post.get("id") == post_id:
            title = post['title'][:50] #only returns the first 50 characters of the title; this is to ensure that it truncates the title in case it is very long
            return templates.TemplateResponse(
                request, "post.html", 
                {"post": post, "title": title})

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

@app.get("/api/posts")
def get_posts():
    return posts

@app.get("/api/posts/{post_id}")
def get_post(post_id: int): # using type hinting helps FastAPI to automatically validate the input
    for post in posts:
        if post.get("id") == post_id:
            return post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

@app.exception_handler(StarletteHTTPException)
def general_http_exception_handler(request: Request, exception: StarletteHTTPException):
    message = (
        exception.detail
        if exception.detail
        else "An error occurred. Please check your request and try again."
    )

    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=exception.status_code,
            content={"detail": message},
        )
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
def validation_exception_handler(request: Request, exception: RequestValidationError):
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"detail": exception.errors()},
        )
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