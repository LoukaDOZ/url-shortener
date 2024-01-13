from fastapi import Request

import time
import random

class Session():
    def __init__(self, sid: str, expiration_date: int):
        self.sid = sid
        self.data = {
            "sid": sid,
            "expiration_date": expiration_date
        }
    
    def set(self, key: str, value: str) -> None:
        self.data[key] = value
    
    def get(self, key: str) -> str:
        return self.data[key] if self.has(key) else None
    
    def delete(self, key: str) -> None:
        self.set(key, None)
    
    def has(self, key: str) -> bool:
        return key in self.data and bool(self.data[key])

class SessionManager():
    SESSION_ID_LEN = 16
    SESSION_ID_CHARS = "ABCDEFGHIJKLMOPQRSTUVWXYZabcdefghijklmopqrstuvwxyz0123456789"
    SESSION_LIFETIME = 10800 # 3 hours in seconds

    def __init__(self):
        self.sessions = []
    
    def get_session(self, request: Request) -> Session:
        has_sid = self.__request_has_sid__(request)
        s = self.__find_session__(request.session["sid"]) if has_sid else None

        if not s or s.get("expiration_date") < int(time.time()):
            s = self.__create_session__(request, int(time.time()) + self.SESSION_LIFETIME)
        
        return s
    
    def __create_session__(self, request: Request, expiration_date: int) -> None:
        sid = self.__generate_session_id__()

        while self.__find_session__(sid) is not None:
            sid = self.__generate_session_id__()
    
        s = Session(sid, expiration_date)
        self.sessions.append(s)
        request.session["sid"] = sid
        return s

    def __find_session__(self, sid: str) -> Session:
        for s in self.sessions:
            if s.sid == sid:
                return s
        return None
    
    def __delete_session__(self, sid: str) -> None:
        s = self.__find_session__(sid)
        if s:
            self.sessions.remove(s)
    
    def __request_has_sid__(self, request: Request) -> bool:
        return "sid" in request.session and bool(request.session["sid"])

    def __generate_session_id__(self) -> str:
        sid = ""
        for i in range(self.SESSION_ID_LEN):
            rand = random.randint(0, len(self.SESSION_ID_CHARS) - 1)
            sid += self.SESSION_ID_CHARS[rand]
        return sid

session_manager = SessionManager()