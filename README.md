# FastBlog

A full-featured blogging web application built with **FastAPI**. The app serves both a REST JSON API for programmatic access and browser-facing HTML pages for end users — both powered by the same backend.

Built as part of a FastAPI tutorial series, this project covers the full lifecycle of a real-world web application: database integration, authentication, file uploads, async operations, and more.

---

## Features

- Browse, create, edit, and delete blog posts
- User registration and login with secure authentication
- Profile picture uploads with automatic image processing
- Paginated post feed
- Dual interface — JSON API for developers, HTML pages for browser users
- Ownership checks — users can only edit or delete their own posts
- Automatic API documentation via Swagger UI and ReDoc

---

## Tech Stack

| Category | Technology |
|---|---|
| Framework | FastAPI |
| Database | SQLite |
| ORM | SQLAlchemy (async) |
| Data Validation | Pydantic |
| Templating | Jinja2 |
| Styling | Bootstrap |
| Authentication | JWT + Argon2 password hashing |
| Image Processing | Pillow |
| Config Management | pydantic-settings |

---

## Getting Started

### Prerequisites

- Python 3.10+
- pip

### Installation

1. Clone the repository
   ```bash
   git clone https://github.com/shalini-agarwal/fastblog.git
   cd fastblog
   ```

2. Create and activate a virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables — create a `.env` file in the root directory
   ```
   SECRET_KEY=your-secret-key-here
   ```
   You can generate a secure secret key with:
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

5. Run the development server
   ```bash
   fastapi dev main.py
   ```

6. Open your browser and visit:
   - App: `http://127.0.0.1:8000`
   - API Docs: `http://127.0.0.1:8000/docs`
   - ReDoc: `http://127.0.0.1:8000/redoc`

---

## Topics Covered

- REST API design with FastAPI
- Jinja2 templating and template inheritance
- Path parameters, query parameters, and request validation
- Pydantic schemas for API contracts (request/response models)
- SQLAlchemy ORM with async support (`aiosqlite`)
- Full CRUD operations (GET, POST, PUT, PATCH, DELETE)
- HTTP status codes and error handling
- Custom exception handlers for API vs browser clients
- Password hashing with Argon2 (one-way, salted)
- JWT authentication — token creation, signing, and verification
- Route protection with FastAPI dependency injection
- Authorization and ownership checks
- File uploads and image processing with Pillow
- Offloading CPU-bound work with `run_in_threadpool`
- Async vs sync routes — when to use each
- Eager loading relationships in async SQLAlchemy
- Code organization with `APIRouter`
- Pagination with `offset` and `limit`
- Separation of concerns — backend owns business logic, frontend owns presentation
- Frontend interactivity using JavaScript and the Fetch API

---

## Project Structure

```
fastblog/
├── routers/
│   ├── __init__.py
│   ├── posts.py
│   └── users.py
├── static/
│   ├── css/
│   ├── icons/
│   ├── js/
│   ├── profile_pics/
│   └── site.webmanifest
├── templates/
│   ├── account.html
│   ├── error.html
│   ├── home.html
│   ├── layout.html
│   ├── login.html
│   ├── post.html
│   ├── register.html
│   └── user_posts.html
├── media/
│   └── profile_pics/
├── populate_images/
├── main.py
├── models.py
├── schemas.py
├── database.py
├── auth.py
├── config.py
├── image_utils.py
├── populate_db.py
└── requirements.txt
```
