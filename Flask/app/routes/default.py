from modules.responses import render, redirect

from modules.session import Session

async def root(session: Session):
    return redirect("/shorten", True)

async def not_found(session: Session):
    return render(session, "not_found.html")