from flask import render_template
from flask import redirect as fredirect

from modules.session import Session

def render(session: Session, page: str, context: dict = {}):
    context["connected"] = bool(session.get("is_connected"))
    return render_template(page, **context)

def redirect(url: str, override_method: bool = False):
    if override_method:
        return fredirect(url)
    return fredirect(url)