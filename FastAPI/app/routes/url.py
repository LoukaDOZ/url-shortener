from fastapi import Request
from fastapi.responses import HTMLResponse

import re
import random

import routes.default as default_routes

from modules.responses import render, redirect
from modules.postgres import query as db
import modules.session as session

# Utils
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

def create_url(request: Request, url_id: str) -> str:
    return f"{request.base_url}r/{url_id}"

# Routes
async def redirect_to_target_url(request: Request, url_id: str) -> HTMLResponse:
    url_id = url_id.strip()
    url = db.get_target_url(url_id)

    if not url:
        return await default_routes.not_found(request)
    return redirect(url)

async def shorten_page(request: Request) -> HTMLResponse:
    print(request.session, session.is_user_connected(request))
    return render(
        request = request,
        page = "index.html",
        context = {
            "connected": session.is_user_connected(request)
        }
    )

async def shorten(request: Request, url: str, guest: bool) -> HTMLResponse:  
    missing_url = False
    failed_url_size = False
    failed_url_regex = False

    if url:
        url = url.strip()
        failed_url_size = not check_url_size(url)
        failed_url_regex = not check_url_regex(url)
    elif not session.is_set(request, "pending_shortening"):
        missing_url = True

    if failed_url_size or failed_url_regex or missing_url:
        context={
            "connected": session.is_user_connected(request),
            "url": url
        }

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
        url_id = session.get(request, "pending_shortening")
        session.delete(request, "pending_shortening")

    if session.is_set(request, "username"):
        username = session.get(request, "username")
    elif not guest:
        session.set(request, "pending_shortening", url_id)
        return redirect(f"/login?shortening=true", True)

    db.insert_url(url, url_id, username)
    return render(
        request = request,
        page = "shortened.html",
        context = {
            "connected": session.is_user_connected(request),
            "shortened_url": create_url(request, url_id)
        }
    )

async def my_urls_page(request: Request) -> HTMLResponse:
    if not session.is_set(request, "username"):
        return redirect("/login")

    query_urls = db.get_user_urls(session.get(request, "username"))
    urls = []

    if query_urls:
        for u in query_urls:
            urls.append({
                "target_url": u[0],
                "shortened_url": create_url(request, u[1])
            })

    return render(
        request = request,
        page = "my_urls.html",
        context = {
            "connected": True,
            "urls": urls
        }
    )