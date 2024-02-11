from flask import Response
from passlib.context import CryptContext

import re

from modules.responses import render, redirect
from modules.postgres import Query as db
from modules.session import session

# Init Passlib hash
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Utils
USERNAME_MIN_LEN = 4
USERNAME_MAX_LEN = 32
USERNAME_REGEX = re.compile("^[-a-zA-Z0-9_@\+=. \*]*$")

PASSWORD_MIN_LEN = 8
PASSWORD_MAX_LEN = 32
PASSWORD_REGEX = re.compile("^[-a-zA-Z0-9@:%_\+~#=.,!~?&\*]*$")

def check_username_size(username: str) -> bool:
    return USERNAME_MIN_LEN <= len(username) <= USERNAME_MAX_LEN

def check_username_regex(username: str) -> bool:
    return USERNAME_REGEX.match(username) is not None

def check_password_size(password: str) -> bool:
    return PASSWORD_MIN_LEN <= len(password) <= PASSWORD_MAX_LEN

def check_password_regex(password: str) -> bool:
    return PASSWORD_REGEX.match(password) is not None

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def compare_password(plain_password: str, hashed_password: str) -> str:
    return pwd_context.verify(plain_password, hashed_password)

# Routes
def login_page(tab: str, shortening: bool) -> Response:
    if session.has("is_connected"):
        session.delete("is_connected")

    return render(
        page = "login.html",
        context = {
            "tab": tab,
            "shortening": shortening
        }
    )

def login(username: str, password: str, shortening: bool) -> Response:
    username = username.strip()
    password = password.strip()
    hashed_password = db.query.get_user_password(username)

    if (not check_username_size(username)
            or not check_username_regex(username)
            or not check_password_size(password)
            or not check_password_regex(password)
            or not hashed_password
            or not compare_password(password, hashed_password)):
        return render(
            page = "login.html",
            context = {
                "tab": "login",
                "shortening": shortening,
                "login_username": username,
                "global_error": "Invalid credentials"
            }
        )
    
    session.set("is_connected", True)
    session.set("username", username)

    if shortening:
        return redirect("/shorten")
    return redirect("/", True)

def register(
        username: str,
        password: str,
        confirm_password: str,
        shortening: bool) -> Response:
    username = username.strip()
    password = password.strip()
    confirm_password = confirm_password.strip()
    error_name = None
    error_message = None

    if not check_username_size(username):
        error_name = "register_username_error"
        error_message = f"Username size should be between {USERNAME_MIN_LEN} and {USERNAME_MAX_LEN} characters"
    elif not check_username_regex(username):
        error_name = "register_username_error"
        error_message = "Username contains invalid characters"
    elif db.query.get_user_password(username):
        error_name = "register_username_error"
        error_message = "Username already exists"
    elif not check_password_size(password):
        error_name = "register_password_error"
        error_message = f"Password size should be between {PASSWORD_MIN_LEN} and {PASSWORD_MAX_LEN} characters"
    elif not check_password_regex(password):
        error_name = "register_password_error"
        error_message = "Password contains invalid characters"
    elif password != confirm_password:
        error_name = "register_confirm_password_error"
        error_message = "Confirmation password does not match"

    if error_name:
        return render(
            page = "login.html",
            context = {
                "tab": "register",
                "shortening": shortening,
                "register_username": username,
                error_name: error_message
            }
        )
    
    db.query.insert_user(username, hash_password(password))
    session.set("is_connected", True)
    session.set("username", username)

    if shortening:
        return redirect("/shorten")
    return redirect("/", True)

def logout() -> Response:
    session.delete("is_connected")
    return redirect("/", True)