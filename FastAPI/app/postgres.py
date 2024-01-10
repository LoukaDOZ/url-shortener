import psycopg2

class DBConnection():
    def __init__(self, connection: psycopg2.extensions.connection):
        self.connection = connection
    
    def insert(self, url: str, url_id: str) -> None:
        cur = self.connection.cursor()
        cur.execute(
            "INSERT INTO url (url_id, target_url) VALUES (%s, %s)",
            (url_id, url)
        )
        self.connection.commit()
        cur.close()

    def get(self, url_id: str) -> str:
        cur = self.connection.cursor()
        cur.execute(
            "SELECT target_url FROM url WHERE url_id = %s",
            (url_id,)
        )
        res = cur.fetchone()
        cur.close()

        return res[0] if res else None

def connect(user: str, password: str, dbname: str, host: str = "localhost", port: int = 5432) -> DBConnection:
    connection = psycopg2.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        dbname=dbname
    )
    return DBConnection(connection)