from fastapi import Request
from fastapi.responses import HTMLResponse

from modules.responses import render, redirect
import modules.session as session

def root(request: Request) -> HTMLResponse:
    return redirect("/shorten/", True)

def not_found(request: Request) -> HTMLResponse:
    return render(
        request = request,
        page = "not_found.html"
    )