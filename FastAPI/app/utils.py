
from fastapi import Request
from passlib.context import CryptContext
import re
import random

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

URL_ID_LEN = 8
URL_ID_CHARS = "ABCDEFGHIJKLMOPQRSTUVWXYZabcdefghijklmopqrstuvwxyz0123456789"

URL_MIN_LEN = 1
URL_MAX_LEN = 512
URL_REGEX = re.compile("^https?:\/\/(www\.)?[-a-zA-Z0-9@:%_\+~#=]{1,256}(\.[a-zA-Z0-9()]{1,6})?(\/[-a-zA-Z0-9()@:%_\+.,!~#?&\/=]*)?$")

USERNAME_MIN_LEN = 4
USERNAME_MAX_LEN = 32
USERNAME_REGEX = re.compile("^[-a-zA-Z0-9_@\+=. \*]*$")

PASSWORD_MIN_LEN = 8
PASSWORD_MAX_LEN = 32
PASSWORD_REGEX = re.compile("^[-a-zA-Z0-9@:%_\+~#=.,!~?&\*]*$")

def generate_url_id() -> str:
    url_id = ""
    for i in range(URL_ID_LEN):
        rand = random.randint(0, len(URL_ID_CHARS) - 1)
        url_id += URL_ID_CHARS[rand]
    return url_id

def check_url_size(url: str) -> bool:
    return URL_MIN_LEN <= len(url) <= URL_MAX_LEN

def check_url_regex(url: str) -> bool:
    return URL_REGEX.match(url) is not None

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

def create_url(request: Request, url_id: str) -> str:
    return f"{request.base_url}r/{url_id}"

def session_key_set(request: Request, key: str) -> bool:
    return key in request.session and request.session[key]

def connected(request: Request) -> bool:
    return session_key_set(request, "username")