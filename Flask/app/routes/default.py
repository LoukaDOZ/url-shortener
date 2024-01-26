from flask import Response

from modules.responses import render, redirect

async def root() -> Response:
    return redirect("/shorten", True)

async def not_found() -> Response:
    return render("not_found.html")