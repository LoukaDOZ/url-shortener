from fastapi import FastAPI, Request, Response, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

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
DB_PORT=9000
DB_USER="admin"
DB_PASSWORD="passwd"

# App init
app = FastAPI(
    version = "1.0.0",
    title = "URL Shortener",
    summary = "Shorten an URL"
)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Jinja init
templates = Jinja2Templates(directory="templates")

# DB connection
query = db.connect(DB_USER, DB_PASSWORD, DB_DEFAULT_DB_NAME, DB_HOST, DB_PORT)

# Routes
@app.get("/", response_class=HTMLResponse)
async def root(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )

@app.get("/{url_id}", response_class=HTMLResponse)
async def redirect(request: Request, url_id: str) -> HTMLResponse:
    url = query.get(url_id)

    if not url:
        return default(request, "")
    return RedirectResponse(url)

@app.post("/shorten", response_class=HTMLResponse)
async def shorten(request: Request, url: Annotated[str, Form()]) -> HTMLResponse:  
    if not utils.validate_url(url):
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "input_error": "Invalid URL",
                "url": url
            }
        )
    
    while True:
        url_id = utils.generate_url_id()
        if not query.get(url_id):
            break
    
    query.insert(url, url_id)
    return templates.TemplateResponse(
        request=request,
        name="shortened.html",
        context={"shortened_url": f"{request.base_url}{url_id}"}
    )

@app.route("/{full_path:path}")
async def default(request: Request, full_path: str = "") -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="not_found.html"
    )
        