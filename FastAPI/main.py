from fastapi import FastAPI, Request, Response, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Annotated
import postgres as db
import re
import random

URL_MAX_LEN = 256
URL_ID_LEN = 16
HOST = "localhost"
PORT = 8000

# App init
app = FastAPI(
    version = "1.0.0",
    title = "URL Shortener",
    summary = "Shorten an URL"
)
#app.mount("/static", StaticFiles(directory="templates"))
templates = Jinja2Templates(directory="templates")
url_regex = re.compile("^https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&\/=]*)$")
url_id_chars = "ABCDEFGHIJKLMOPQRSTUVWXYZabcdefghijklmopqrstuvwxyz0123456789"

# DB connection init
query = db.connect("postgres", "postgres", "url_shortener", "localhost", 5431)

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
    if len(url) > URL_MAX_LEN:
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
        context={"shortened_url": f"http://{HOST}:{PORT}/{url_id}"}
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
        rand = random.randint(0, len(url_id_chars) - 1)
        url_id += url_id_chars[rand]
    return url_id
        