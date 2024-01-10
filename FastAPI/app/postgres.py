import psycopg2

class DBConnection():
    def __init__(self, connection):
        self.connection = connection
    
    def insert(self, url, url_id):
        cur = self.connection.cursor()
        cur.execute(
            "INSERT INTO url (url_id, target_url) VALUES (%s, %s)",
            (url_id, url)
        )
        self.connection.commit()
        cur.close()

    def get(self, url_id):
        cur = self.connection.cursor()
        cur.execute(
            "SELECT target_url FROM url WHERE url_id = %s",
            (url_id,)
        )
        res = cur.fetchone()
        cur.close()

        return res[0] if res else None

def connect(user, password, dbname, host = "localhost", port = 5432):
    connection = psycopg2.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        dbname=dbname
    )
    return DBConnection(connection)