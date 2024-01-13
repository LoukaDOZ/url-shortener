from fastapi import Request

def set(request: Request, key: str, value: str) -> None:
    request.session[key] = value

def delete(request: Request, key: str) -> None:
    request.session[key] = None

def get(request: Request, key: str) -> str:
    return request.session[key]

def is_set(request: Request, key: str) -> bool:
    return key in request.session and bool(request.session[key])

def connect_user(request: Request, username: str) -> None:
    set(request, "username", username)

def disconnect_user(request: Request) -> None:
    delete(request, "username")

def is_user_connected(request: Request) -> bool:
    return is_set(request, "username")