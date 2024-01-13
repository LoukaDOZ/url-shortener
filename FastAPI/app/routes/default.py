from fastapi import Request
from fastapi.responses import HTMLResponse

from modules.responses import render, redirect
import modules.session as session

async def root(request: Request) -> HTMLResponse:
    return redirect("/shorten", True)

async def not_found(request: Request) -> HTMLResponse:
    return render(
        request = request,
        page = "not_found.html",
        context = {
            "connected": session.is_user_connected(request)
        }
    )