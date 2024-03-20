from fastapi import Request
from fastapi.responses import HTMLResponse

from datetime import datetime
import time
import random
import re

import routes.default as default_routes

from modules.responses import render, redirect
from modules.postgres import query as db
from modules.session import session_manager as session

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

def create_url(request: Request, url_id: str) -> str:
    return f"{request.base_url}r/{url_id}"

def remove_expired_urls():
    db.delete_expired_urls(int(time.time()))

# Routes
def redirect_to_target_url(request: Request, url_id: str) -> HTMLResponse:
    url_id = url_id.strip()

    remove_expired_urls()
    url = db.get_target_url(url_id)

    if not url:
        return default_routes.not_found(request)
    return redirect(url)

def shorten_page(request: Request) -> HTMLResponse:
    return render(
        request = request,
        page = "index.html"
    )

def shorten(request: Request, url: str, guest: bool) -> HTMLResponse:  
    missing_url = False
    failed_url_size = False
    failed_url_regex = False
    user_session = session.get_session(request)

    if url:
        url = url.strip()
        failed_url_size = not check_url_size(url)
        failed_url_regex = not check_url_regex(url)
    elif not user_session.has("pending_url_id"):
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
            request = request,
            page = "index.html",
            context = context
        )

    url_id = None
    username = None

    if url:
        while True:
            url_id = generate_url_id()
            if not db.get_target_url(url_id):
                break
    else:
        url_id = user_session.get("pending_url_id")
        url = user_session.get("pending_target_url")
        user_session.delete("pending_url_id")
        user_session.delete("pending_target_url")

    if user_session.has("is_connected"):
        username = user_session.get("username")
    elif not guest:
        user_session.set("pending_url_id", url_id)
        user_session.set("pending_target_url", url)
        return redirect(f"/login/?shortening=true", True)

    expiration_date = get_url_expiration_date()
    db.insert_url(url, url_id, expiration_date, username)
    return render(
        request = request,
        page = "shortened.html",
        context = {
            "shortened_url": create_url(request, url_id),
            "expiration_date": date_to_str(expiration_date)
        }
    )

def my_urls_page(request: Request) -> HTMLResponse:
    user_session = session.get_session(request)

    if not user_session.has("is_connected"):
        return redirect("/login/")

    query_urls = db.get_user_urls(user_session.get("username"))
    urls = []

    if query_urls:
        for u in query_urls:
            urls.append({
                "target_url": u[0],
                "shortened_url": create_url(request, u[1]),
                "expiration_date": date_to_str(u[2])
            })

    return render(
        request = request,
        page = "my_urls.html",
        context = { "urls": urls }
    )