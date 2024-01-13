from fastapi import Request

def set(request: Request, key: str, value: str) -> None:
    request.session[key] = value

def delete(request: Request, key: str) -> None:
    request.session[key] = None

def get(request: Request, key: str) -> str:
    return request.session[key]

def is_set(request: Request, key: str) -> bool:
    return key in request.session and request.session[key]

def is_connected(request: Request):
    return is_set(request, "username")