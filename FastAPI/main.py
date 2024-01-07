from fastapi import FastAPI, Request, Response, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Annotated
import postgres as db
import re
import random

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
        request=request, name="index.html"
    )

@app.get("/{url_id}")
def redirect(url_id):
    url = query.get(url_id)

    if not url:
        return "Invalid shortened URL"

    return url

@app.post("/shorten")
def shorten(url: Annotated[str, Form()]):
    if len(url) > 256:
        return "Invalid URL"
    
    while True:
        url_id = generate_url_id()
        if not query.get(url_id):
            break
    
    query.insert(url, url_id)
    return url_id

def generate_url_id():
    url_id = ""
    for i in range(16):
        rand = random.randint(0, len(url_id_chars) - 1)
        url_id += url_id_chars[rand]
    return url_id
        