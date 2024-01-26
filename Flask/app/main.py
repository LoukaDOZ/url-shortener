from flask import Flask, request, session, abort, Response

from modules.session import session_manager, Session
import modules.postgres as db

import routes.default as default_routes
import routes.login as login_routes
import routes.url as url_routes

# App init
app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# DB init
db.init(app)

def get_session() -> Session:
    return session_manager.get_session(session)

def get_form(key: str, placeholder: object) -> object:
    return request.form.get(key) if key in request.form else placeholder

def get_args(key: str, placeholder: object) -> object:
    return request.args.get(key) if key in request.args else placeholder

# Routes
@app.route("/", methods=["GET"])
async def root() -> Response:
    return await default_routes.root(get_session())

@app.route("/r/<string:url_id>", methods=["GET"])
async def redirect(url_id: str) -> Response:
    return await url_routes.redirect_to_target_url(get_session(), url_id)

@app.route("/shorten", methods=["GET", "POST"])
async def shorten() -> Response:
    if request.method == "POST":
        url = get_form("url", "")
        guest = bool(get_args("guest", False))
        return await url_routes.shorten(get_session(), request.url_root, url, guest)
    
    return await url_routes.shorten_page(get_session())

@app.route("/login", methods=["GET", "POST"])
async def login() -> Response:
    shortening = bool(get_args("shortening", False))
    print(shortening)

    if request.method == "POST":
        username = get_form("username", "")
        password = get_form("password", "")
        return await login_routes.login(get_session(), username, password, shortening)
    
    tab = get_args("tab", "login")
    return await login_routes.login_page(get_session(), tab, shortening)

@app.post("/register")
async def register() -> Response:
    username = get_form("username", "")
    password = get_form("password", "")
    confirm_password = get_form("confirm_password", "")
    shortening = bool(get_args("shortening", False))

    return await login_routes.register(
        get_session(), username, password, confirm_password, shortening
    )

@app.get("/logout")
async def logout() -> Response:
    return await login_routes.logout(get_session())

@app.get("/my-urls")
async def my_urls() -> Response:
    return await url_routes.my_urls_page(get_session(), request.url_root)

@app.route("/<path:unknown_path>")
async def not_found(unknown_path: str) -> Response:
    abort(404)

@app.errorhandler(404)
async def page_not_found(error) -> Response:
    return await default_routes.not_found(get_session()), 404