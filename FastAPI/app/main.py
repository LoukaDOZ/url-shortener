from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from typing import Annotated
import os

import routes.default as default_routes
import routes.login as login_routes
import routes.url as url_routes

# App init
app = FastAPI(
    version = "1.0.0",
    title = "URL Shortener",
    summary = "Shorten an URL"
)
app.add_middleware(SessionMiddleware, secret_key=os.urandom(32))
app.mount("/static", StaticFiles(directory="static"), name="static")

# Routes
@app.get("/", response_class=HTMLResponse)
async def root(request: Request) -> HTMLResponse:
    return await default_routes.root(request)

@app.get("/r/{url_id}", response_class=HTMLResponse)
async def redirect(request: Request, url_id: str) -> HTMLResponse:
    return await url_routes.redirect_to_target_url(request, url_id)

@app.get("/shorten", response_class=HTMLResponse)
async def shorten_page(request: Request) -> HTMLResponse:
    print(request.session)
    return await url_routes.shorten_page(request)

@app.post("/shorten", response_class=HTMLResponse)
async def shorten(request: Request,
        url: Annotated[str, Form()] = "",
        guest: bool = False) -> HTMLResponse:  
    return await url_routes.shorten(request, url, guest)

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, 
        tab: str = "login",
        shortening: bool = False) -> HTMLResponse:
    return await login_routes.login_page(request, tab, shortening)

@app.post("/login", response_class=HTMLResponse)
async def login(request: Request,
        username: Annotated[str, Form()],
        password: Annotated[str, Form()],
        shortening: bool = False) -> HTMLResponse:
    return await login_routes.login(request, username, password, shortening)

@app.post("/register", response_class=HTMLResponse)
async def register(request: Request,
        username: Annotated[str, Form()],
        password: Annotated[str, Form()],
        confirm_password: Annotated[str, Form()],
        shortening: bool = False) -> HTMLResponse:
    return await login_routes.register(request, username, password, confirm_password, shortening)

@app.get("/logout", response_class=HTMLResponse)
async def logout(request: Request) -> HTMLResponse:
    return await login_routes.logout(request)

@app.get("/my-urls", response_class=HTMLResponse)
async def my_urls_page(request: Request) -> HTMLResponse:
    return await url_routes.my_urls_page(request)

@app.route("/{full_path:path}")
async def default(request: Request, full_path: str = "") -> HTMLResponse:
    return await default_routes.not_found(request)
        