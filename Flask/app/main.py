from flask import Flask, request, abort, Response, flash
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from datetime import timedelta
import os

from modules.postgres import Query, DBConnection

import routes.default as default_routes
import routes.login as login_routes
import routes.url as url_routes

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_DEFAULT_DB_NAME = os.getenv("DB_DEFAULT_DB_NAME", "url_shortener")

# App init
app = Flask(__name__)

# DB init
uri = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DEFAULT_DB_NAME}"
app.config["SQLALCHEMY_DATABASE_URI"] = uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
Query.query = DBConnection(db, app.app_context())

# Session init
app.config["SESSION_TYPE"] = "sqlalchemy"
app.config["SESSION_SQLALCHEMY"] = db
app.config["SESSION_SQLALCHEMY_TABLE"] = "session"
app.config["SESSION_PERMANENT"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)
app.config["SESSION_AUTODELETE"] = True
with app.app_context():
    session = Session(app)

# Create tables if not exist
with app.app_context():
    db.create_all()
    session.app.session_interface.db.create_all()

def get_form(key: str, placeholder: object) -> object:
    return request.form.get(key) if key in request.form else placeholder

def get_args(key: str, placeholder: object) -> object:
    return request.args.get(key) if key in request.args else placeholder

# Routes
@app.route("/", methods=["GET"])
async def root() -> Response:
    return await default_routes.root()

@app.route("/r/<string:url_id>", methods=["GET"])
async def redirect(url_id: str) -> Response:
    return await url_routes.redirect_to_target_url(url_id)

@app.route("/shorten", methods=["GET", "POST"])
async def shorten() -> Response:
    if request.method == "POST":
        url = get_form("url", "")
        guest = bool(get_args("guest", False))
        return await url_routes.shorten(request.url_root, url, guest)
    
    return await url_routes.shorten_page()

@app.route("/login", methods=["GET", "POST"])
async def login() -> Response:
    shortening = bool(get_args("shortening", False))

    if request.method == "POST":
        username = get_form("username", "")
        password = get_form("password", "")
        return await login_routes.login(username, password, shortening)
    
    tab = get_args("tab", "login")
    return await login_routes.login_page(tab, shortening)

@app.post("/register")
async def register() -> Response:
    username = get_form("username", "")
    password = get_form("password", "")
    confirm_password = get_form("confirm_password", "")
    shortening = bool(get_args("shortening", False))

    return await login_routes.register(
        username, password, confirm_password, shortening
    )

@app.get("/logout")
async def logout() -> Response:
    return await login_routes.logout()

@app.get("/my-urls")
async def my_urls() -> Response:
    return await url_routes.my_urls_page(request.url_root)

@app.route("/<path:unknown_path>")
async def not_found(unknown_path: str) -> Response:
    abort(404)

@app.errorhandler(404)
async def page_not_found(error) -> Response:
    return await default_routes.not_found(), 404