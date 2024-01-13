from fastapi import FastAPI, Request, Response, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import starlette.status as status

from typing import Annotated
import os
import re
import random

import postgres as db
import utils

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_DEFAULT_DB_NAME = os.getenv("DB_DEFAULT_DB_NAME", "url_shortener")

# App init
app = FastAPI(
    version = "1.0.0",
    title = "URL Shortener",
    summary = "Shorten an URL"
)
app.add_middleware(SessionMiddleware, secret_key=os.urandom(32))
app.mount("/static", StaticFiles(directory="static"), name="static")

# Jinja init
templates = Jinja2Templates(directory="templates")

# DB connection
query = db.connect(DB_USER, DB_PASSWORD, DB_DEFAULT_DB_NAME, DB_HOST, DB_PORT)

# Routes
@app.get("/", response_class=HTMLResponse)
async def root(request: Request) -> HTMLResponse:
    print(request.session)
    return RedirectResponse("/shorten", status_code=status.HTTP_302_FOUND)

@app.get("/r/{url_id}", response_class=HTMLResponse)
async def redirect(request: Request, url_id: str) -> HTMLResponse:
    url_id = url_id.strip()
    url = query.get_target_url(url_id)

    if not url:
        return await default(request, "")
    return RedirectResponse(url)

@app.get("/shorten", response_class=HTMLResponse)
async def root(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "connected": utils.connected(request)
        }
    )

@app.post("/shorten", response_class=HTMLResponse)
async def shorten(request: Request,
        url: Annotated[str, Form()] = "",
        guest: bool = False) -> HTMLResponse:  
    missing_url = False
    failed_url_size = False
    failed_url_regex = False

    if url:
        url = url.strip()
        failed_url_size = not utils.check_url_size(url)
        failed_url_regex = not utils.check_url_regex(url)
    elif not utils.session_key_set(request, "pending_shortening"):
        missing_url = True

    if failed_url_size or failed_url_regex or missing_url:
        context={
            "connected": utils.connected(request),
            "url": url
        }

        if missing_url:
            context["global_error"] = "An error has occur"
        elif failed_url_regex:
            context["input_error"] = "Invalid URL"
        else:
            context["input_error"] = "URL is too long"

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context=context
        )

    url_id = None
    username = None

    if url:    
        while True:
            url_id = utils.generate_url_id()
            if not query.get_target_url(url_id):
                break
    else:
        url_id = request.session["pending_shortening"]
        request.session["pending_shortening"] = None

    if utils.session_key_set(request, "username"):
        username = request.session["username"]
    elif not guest:
        request.session["pending_shortening"] = url_id
        return RedirectResponse(f"/login?shortening=true", status_code=status.HTTP_302_FOUND)

    query.insert_url(url, url_id, username)
    return templates.TemplateResponse(
        request=request,
        name="shortened.html",
        context={
            "connected": utils.connected(request),
            "shortened_url": utils.create_url(request, url_id)
        }
    )

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, 
        tab: str = "login",
        shortening: bool = False) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "tab": tab,
            "shortening": shortening
        }
    )

@app.post("/login", response_class=HTMLResponse)
async def login(request: Request,
        username: Annotated[str, Form()],
        password: Annotated[str, Form()],
        shortening: bool = False) -> HTMLResponse:
    username = username.strip()
    password = password.strip()
    hashed_password = query.get_user_password(username)

    if (not utils.check_username_size(username)
            or not utils.check_username_regex(username)
            or not utils.check_password_size(password)
            or not utils.check_password_regex(password)
            or not hashed_password
            or not utils.compare_password(password, hashed_password)):
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "tab": "login",
                "shortening": shortening,
                "login_username": username,
                "global_error": "Invalid credentials"
            }
        )
    
    request.session["username"] = username
    if shortening:
        return RedirectResponse("/shorten")

    return RedirectResponse("/", status_code=status.HTTP_302_FOUND)

@app.post("/register", response_class=HTMLResponse)
async def register(request: Request,
        username: Annotated[str, Form()],
        password: Annotated[str, Form()],
        confirm_password: Annotated[str, Form()],
        shortening: bool = False) -> HTMLResponse:
    username = username.strip()
    password = password.strip()
    confirm_password = confirm_password.strip()
    error_name = None
    error_message = None

    if not utils.check_username_size(username):
        error_name = "register_username_error"
        error_message = f"Username size should be between {utils.USERNAME_MIN_LEN} and {utils.USERNAME_MAX_LEN} characters"
    elif not utils.check_username_regex(username):
        error_name = "register_username_error"
        error_message = "Username contains invalid characters"
    elif query.get_user_password(username):
        error_name = "register_username_error"
        error_message = "Username already exists"
    elif not utils.check_password_size(password):
        error_name = "register_password_error"
        error_message = f"Password size should be between {utils.PASSWORD_MIN_LEN} and {utils.PASSWORD_MAX_LEN} characters"
    elif not utils.check_password_regex(password):
        error_name = "register_password_error"
        error_message = "Password contains invalid characters"
    elif password != confirm_password:
        error_name = "register_confirm_password_error"
        error_message = "Confirmation password does not match"

    if error_name:
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "tab": "register",
                "shortening": shortening,
                "register_username": username,
                error_name: error_message
            }
        )
    
    query.insert_user(username, utils.hash_password(password))
    if shortening:
        return RedirectResponse("/shorten")
    
    return RedirectResponse("/", status_code=status.HTTP_302_FOUND)

@app.get("/disconnect", response_class=HTMLResponse)
async def disconect(request: Request) -> HTMLResponse:
    request.session["username"] = None
    return RedirectResponse("/", status_code=status.HTTP_302_FOUND)

@app.get("/my-urls", response_class=HTMLResponse)
async def my_urls_page(request: Request) -> HTMLResponse:
    if not utils.connected(request):
        return RedirectResponse("/login")

    query_urls = query.get_user_urls(request.session["username"])
    urls = []

    if query_urls:
        for u in query_urls:
            urls.append({
                "target_url": u[0],
                "shortened_url": utils.create_url(request, u[1])
            })

    return templates.TemplateResponse(
        request=request,
        name="my_urls.html",
        context={
            "connected": True,
            "urls": urls
        }
    )

@app.route("/{full_path:path}")
async def default(request: Request, full_path: str = "") -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="not_found.html",
        context={
            "connected": utils.connected(request)
        }
    )
        