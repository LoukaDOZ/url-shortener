from flask import render_template, Response
from flask import redirect as fredirect

from modules.session import session

def render(page: str, context: dict = {}) -> Response:
    context["connected"] = bool(session.get("is_connected"))
    return render_template(page, **context)

def redirect(url: str, override_method: bool = False) -> Response:
    if override_method:
        return fredirect(url, code=302)
    return fredirect(url, code=307)