from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

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

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
@app.get("/posts", response_class=HTMLResponse, include_in_schema=False)
def home():
    return f"<h1>{posts[0]['title']}</h1>"

@app.get("/api/posts")
def get_posts():
    return posts
