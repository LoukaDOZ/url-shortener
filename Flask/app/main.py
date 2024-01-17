from flask import Flask, request, session

from modules.session import session_manager, Session

import routes.default as default_routes
import routes.login as login_routes
import routes.url as url_routes

# App init
app = Flask(__name__)

def get_session() -> Session:
    return session_manager.get_session(session)

def get_form(key: str, placeholder: object) -> object:
    return request.form.get(key)

# Routes
@app.route("/", methods=["GET"])
async def root():
    return await default_routes.root(get_session())

@app.route("/r/{url_id}", methods=["GET"])
async def redirect(url_id: str):
    return await url_routes.redirect_to_target_url(get_session(), url_id)

@app.route("/shorten", methods=["GET", "POST"])
async def shorten():
    if request.method == "POST":
        url = request.form.get("url")
        return await url_routes.shorten(get_session(), request.base_url, url, guest)
    return await url_routes.shorten_page(get_session())

@app.route("/login", methods=["GET", "POST"])
async def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        return await login_routes.login(get_session(), username, password, shortening)
    return await login_routes.login_page(get_session(), tab, shortening)

@app.post("/register")
async def register():
    username = request.form.get("username")
    password = request.form.get("password")
    confirm_password = request.form.get("confirm_password")
    return await login_routes.register(
        get_session(), username, password, confirm_password, shortening
    )

@app.get("/logout")
async def logout():
    return await login_routes.logout(get_session())

@app.get("/my-urls")
async def my_urls():
    return await url_routes.my_urls_page(get_session(), request.base_url)

@app.route("/<path:unknown_path>")
async def not_found(unknown_path: str):
    abort(404)

@app.errorhandler(404)
async def page_not_found(error):
    return default_routes.not_found(get_session()), 404