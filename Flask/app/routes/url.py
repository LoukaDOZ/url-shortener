from flask import abort, Response

from datetime import datetime
import time
import random
import re

import routes.default as default_routes

from modules.responses import render, redirect
from modules.postgres import Query as db
from modules.session import session

# Utils
URL_LIFETIME = 604800 # 7 days in seconds

URL_ID_LEN = 8
URL_ID_CHARS = "ABCDEFGHIJKLMOPQRSTUVWXYZabcdefghijklmopqrstuvwxyz0123456789"

URL_MIN_LEN = 1
URL_MAX_LEN = 512
URL_REGEX = re.compile("^https?:\/\/(www\.)?[-a-zA-Z0-9@:%_\+~#=]{1,256}(\.[a-zA-Z0-9()]{1,6})?(\/[-a-zA-Z0-9()@:%_\+.,!~#?&\/=]*)?$")

def check_url_size(url: str) -> bool:
    return URL_MIN_LEN <= len(url) <= URL_MAX_LEN

def check_url_regex(url: str) -> bool:
    return URL_REGEX.match(url) is not None

def generate_url_id() -> str:
    url_id = ""
    for i in range(URL_ID_LEN):
        rand = random.randint(0, len(URL_ID_CHARS) - 1)
        url_id += URL_ID_CHARS[rand]
    return url_id

def get_url_expiration_date():
    return int(time.time()) + URL_LIFETIME

def date_to_str(date: int):
    return datetime.fromtimestamp(date).strftime("%d/%m/%Y %H:%M")

def create_url(base_url: str, url_id: str) -> str:
    return f"{base_url}r/{url_id}"

def remove_expired_urls():
    db.query.delete_expired_urls(int(time.time()))

# Routes
async def redirect_to_target_url(url_id: str) -> Response:
    url_id = url_id.strip()

    remove_expired_urls()
    url = db.query.get_target_url(url_id)

    if not url:
        abort(404)
    return redirect(url)

from flask import session as fsession
async def shorten_page() -> Response:
    return render("index.html")

async def shorten(base_url: str, url: str, guest: bool) -> Response:
    missing_url = False
    failed_url_size = False
    failed_url_regex = False

    if url:
        url = url.strip()
        failed_url_size = not check_url_size(url)
        failed_url_regex = not check_url_regex(url)
    elif not session.has("pending_url_id"):
        missing_url = True

    if failed_url_size or failed_url_regex or missing_url:
        context={ "url": url }

        if missing_url:
            context["global_error"] = "An error has occur"
        elif failed_url_regex:
            context["input_error"] = "Invalid URL"
        else:
            context["input_error"] = "URL is too long"

        return render(
            page = "index.html",
            context = context
        )

    url_id = None
    username = None

    if url:
        while True:
            url_id = generate_url_id()
            if not db.query.get_target_url(url_id):
                break
    else:
        url_id = session.get("pending_url_id")
        url = session.get("pending_target_url")
        session.delete("pending_url_id")
        session.delete("pending_target_url")

    if session.has("is_connected"):
        username = session.get("username")
    elif not guest:
        session.set("pending_url_id", url_id)
        session.set("pending_target_url", url)
        return redirect(f"/login?shortening=true", True)

    expiration_date = get_url_expiration_date()
    db.query.insert_url(url, url_id, expiration_date, username)
    return render(
        page = "shortened.html",
        context = {
            "shortened_url": create_url(base_url, url_id),
            "expiration_date": date_to_str(expiration_date)
        }
    )

async def my_urls_page(base_url: str) -> Response:
    if not session.has("is_connected"):
        return redirect("/login")

    query_urls = db.query.get_user_urls(session.get("username"))
    urls = []

    if query_urls:
        for u in query_urls:
            urls.append({
                "target_url": u[0],
                "shortened_url": create_url(base_url, u[1]),
                "expiration_date": date_to_str(u[2])
            })

    return render(
        page = "my_urls.html",
        context = { "urls": urls })