from flask import Response

from modules.responses import render, redirect

from modules.session import Session

async def root(session: Session) -> Response:
    return redirect("/shorten", True)

async def not_found(session: Session) -> Response:
    return render(session, "not_found.html")