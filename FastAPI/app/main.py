from fastapi import FastAPI, Request, Response, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Annotated
import postgres as db
import os
import re
import random

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_DEFAULT_DB_NAME = os.getenv("DB_DEFAULT_DB_NAME", "url_shortener")
JINJA_TEMPLATES_FOLDER = "templates"
URL_ID_LEN = 16
URL_REGEX = re.compile("^https?:\/\/(www\.)?[-a-zA-Z0-9@:%_\+~#=]{1,256}(\.[a-zA-Z0-9()]{1,6})?(\/[-a-zA-Z0-9()@:%_\+.~#?&\/=]*)?$")
URL_ID_CHARS = "ABCDEFGHIJKLMOPQRSTUVWXYZabcdefghijklmopqrstuvwxyz0123456789"

# App init
app = FastAPI(
    version = "1.0.0",
    title = "URL Shortener",
    summary = "Shorten an URL"
)
#app.mount("/static", StaticFiles(directory="templates"))
templates = Jinja2Templates(directory=JINJA_TEMPLATES_FOLDER)

# DB connection init
query = db.connect(DB_USER, DB_PASSWORD, DB_DEFAULT_DB_NAME, DB_HOST, DB_PORT)

# Routes
@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )

@app.get("/{url_id}", response_class=HTMLResponse)
def redirect(request: Request, url_id):
    url = query.get(url_id)

    if not url:
        return default(request, "")
    return RedirectResponse(url)

@app.post("/shorten", response_class=HTMLResponse)
def shorten(request: Request, url: Annotated[str, Form()]):
    if not URL_REGEX.match(url):
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "error_message": "Invalid URL",
                "url": url
            }
        )
    
    while True:
        url_id = generate_url_id()
        if not query.get(url_id):
            break
    
    query.insert(url, url_id)
    return templates.TemplateResponse(
        request=request,
        name="shortened.html",
        context={"shortened_url": f"{request.base_url}{url_id}"}
    )

@app.route("/{full_path:path}")
def default(request: Request, full_path: str):
    return templates.TemplateResponse(
        request=request,
        name="not_found.html"
    ) 

def generate_url_id():
    url_id = ""
    for i in range(URL_ID_LEN):
        rand = random.randint(0, len(URL_ID_CHARS) - 1)
        url_id += URL_ID_CHARS[rand]
    return url_id
        