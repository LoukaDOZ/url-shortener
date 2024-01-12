import psycopg2

class DBConnection():
    def __init__(self, connection: psycopg2.extensions.connection):
        self.connection = connection
    
    def insert_url(self, url: str, url_id: str, username: str = None) -> None:
        cur = self.connection.cursor()

        if username:
            cur.execute(
                "INSERT INTO url (url_id, target_url, username) VALUES (%s, %s, %s)",
                (url_id, url, username)
            )
        else:
            cur.execute(
                "INSERT INTO url (url_id, target_url) VALUES (%s, %s)",
                (url_id, url)
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

    def insert_user(self, username: str, hash_password: str):
        cur = self.connection.cursor()
        cur.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            (username, hash_password)
        )
        self.connection.commit()
        cur.close()

    def get_user_password(self, username: str):
        cur = self.connection.cursor()
        cur.execute(
            "SELECT password FROM users WHERE username = %s",
            (username,)
        )
        res = cur.fetchone()
        cur.close()

        return res[0] if res else None

    def get_user_urls(self, username: str) -> str:
        cur = self.connection.cursor()
        cur.execute(
            "SELECT target_url, url_id FROM url WHERE username = %s",
            (username,)
        )

        res = [cur.fetchone() for i in range(cur.rowcount)]
        cur.close()
        return res

def connect(user: str, password: str, dbname: str, host: str = "localhost", port: int = 5432) -> DBConnection:
    connection = psycopg2.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        dbname=dbname
    )
    return DBConnection(connection)