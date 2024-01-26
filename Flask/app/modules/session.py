from flask import session as fsession

class Session():
    def set(self, key: str, value: str) -> None:
        fsession[key] = value
        fsession.modified = True
        print("----", key, value, fsession, fsession.sid, fsession.new, fsession[key], fsession.modified)
    
    def get(self, key: str) -> str:
        print("====", key, fsession, fsession.sid, fsession.new, (fsession[key] if key in fsession else "nope"), fsession.modified)
        return fsession[key] if self.has(key) else None
    
    def delete(self, key: str) -> None:
        self.set(key, None)
    
    def has(self, key: str) -> bool:
        return key in fsession and bool(fsession[key])

session = Session()