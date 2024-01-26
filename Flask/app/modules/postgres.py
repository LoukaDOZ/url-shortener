from flask import Flask
from flask.ctx import AppContext
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, BigInteger, ForeignKey
from sqlalchemy.orm import DeclarativeBase, mapped_column

import os

class Query():
    query = None

class DBConnection():
    def __init__(self, db: SQLAlchemy, context: AppContext):
        self.db = db
        self.session = db.session
        self.context = context
    
    def insert_url(self, url: str, url_id: str, expiration_date: int, username: str = None) -> None:
        data = URL(
            _id = url_id,
            target = url,
            expiration = expiration_date,
            username = username if username else None
        )
        
        with self.context:
            self.session.add(data)
            self.session.commit()

    def get_target_url(self, url_id: str) -> str:
        stmt = self.db.select(URL).where(URL._id == url_id)

        with self.context:
            res = self.session.execute(stmt).all()

        return res[0][0].target if len(res) > 0 else None
    
    def delete_expired_urls(self, current_date: int) -> None:
        stmt = self.db.delete(URL).where(URL.expiration < current_date)

        with self.context:
            res = self.session.execute(stmt)

    def insert_user(self, username: str, hash_password: str) -> None:
        data = User(
            username = username,
            password = hash_password
        )
        
        with self.context:
            self.session.add(data)
            self.session.commit()

    def get_user_password(self, username: str) -> str:
        stmt = self.db.select(User).where(User.username == username)

        with self.context:
            res = self.session.execute(stmt).all()

        return res[0][0].password if len(res) > 0 else None

    def get_user_urls(self, username: str) -> list:
        stmt = self.db.select(URL).where(URL.username == username)

        with self.context:
            res = self.session.execute(stmt).all()

        return [(i[0].target, i[0]._id, i[0].expiration) for i in res]

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    username = mapped_column("username", String(32), primary_key=True, nullable=False)
    password = mapped_column("password", String(64), nullable=False)

class URL(Base):
    __tablename__ = "url"
    
    _id = mapped_column("url_id", String(8), primary_key=True, nullable=False)
    target = mapped_column("target_url", String(512), nullable=False)
    expiration = mapped_column("expiration_date", BigInteger, nullable=False)
    username = mapped_column(ForeignKey("users.username"), nullable=True)

def init(app: Flask) -> None:
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", 5432))
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
    DB_DEFAULT_DB_NAME = os.getenv("DB_DEFAULT_DB_NAME", "url_shortener")

    uri = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DEFAULT_DB_NAME}"
    app.config["SQLALCHEMY_DATABASE_URI"] = uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db = SQLAlchemy(model_class = Base)
    db.init_app(app)

    with app.app_context():
        db.create_all()
    
    Query.query = DBConnection(db, app.app_context())
    print("DB INITIALIZED")