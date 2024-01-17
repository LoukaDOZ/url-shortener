import psycopg2

import os

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_DEFAULT_DB_NAME = os.getenv("DB_DEFAULT_DB_NAME", "url_shortener")

class DBConnection():
    def __init__(self, connection: psycopg2.extensions.connection):
        self.connection = connection
    
    def insert_url(self, url: str, url_id: str, expiration_date: int, username: str = None) -> None:
        cur = self.connection.cursor()

        if username:
            cur.execute(
                "INSERT INTO url (url_id, target_url, expiration_date, username) VALUES (%s, %s, %s, %s)",
                (url_id, url, expiration_date, username)
            )
        else:
            cur.execute(
                "INSERT INTO url (url_id, target_url, expiration_date) VALUES (%s, %s, %s)",
                (url_id, url, expiration_date)
            )

        self.connection.commit()
        cur.close()

    def get_target_url(self, url_id: str) -> str:
        cur = self.connection.cursor()
        cur.execute(
            "SELECT target_url FROM url WHERE url_id = %s",
            (url_id,)
        )
        res = cur.fetchone()
        cur.close()

        return res[0] if res else None
    
    def delete_expired_urls(self, current_date: int) -> None:
        cur = self.connection.cursor()
        cur.execute(
            "DELETE FROM url WHERE expiration_date < %s",
            (current_date, )
        )
        self.connection.commit()
        cur.close()

    def insert_user(self, username: str, hash_password: str) -> None:
        cur = self.connection.cursor()
        cur.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            (username, hash_password)
        )
        self.connection.commit()
        cur.close()

    def get_user_password(self, username: str) -> str:
        cur = self.connection.cursor()
        cur.execute(
            "SELECT password FROM users WHERE username = %s",
            (username,)
        )
        res = cur.fetchone()
        cur.close()

        return res[0] if res else None

    def get_user_urls(self, username: str) -> list:
        cur = self.connection.cursor()
        cur.execute(
            "SELECT target_url, url_id, expiration_date FROM url WHERE username = %s",
            (username,)
        )

        res = [cur.fetchone() for i in range(cur.rowcount)]
        cur.close()
        return res

query = DBConnection(
    psycopg2.connect(
        host = DB_HOST,
        port = DB_PORT,
        user = DB_USER,
        password = DB_PASSWORD,
        dbname = DB_DEFAULT_DB_NAME
    )
)