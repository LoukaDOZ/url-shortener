from flask import Response

from modules.responses import render, redirect

def root() -> Response:
    return redirect("/shorten", True)

def not_found() -> Response:
    return render("not_found.html")