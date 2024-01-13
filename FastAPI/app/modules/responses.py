from fastapi import Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import starlette.status as status

from modules.session import is_user_connected

# Jinja init
templates = Jinja2Templates(directory="templates")

def render(request: Request, page: str, context: dict = {}) -> HTMLResponse:
    context["connected"] = is_user_connected(request)

    return templates.TemplateResponse(
        request = request,
        name = page,
        context = context
    )

def redirect(url: str, override_method: bool = False) -> RedirectResponse:
    if override_method:
        return RedirectResponse(url, status_code = status.HTTP_302_FOUND)
    return RedirectResponse(url)