from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

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
    return templates.TemplateResponse(request, "home.html", {"posts": posts, "title": "Home"})

@app.get("/api/posts")
def get_posts():
    return posts
