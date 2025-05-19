import mariadb

class DBConnection:
    def __init__(self):
        try:
            self.conn = mariadb.connect(
                user="Admin",
                password="Admin1",
                host="localhost",
                port=3306,
                database="versicherung"
            )
            self.cur = self.conn.cursor()
        except mariadb.Error as e:
            print(f"Fehler bei der Verbindung: {e}")
            exit(1)

    def get_cursor(self):
        return self.cur

    def commit(self):
        self.conn.commit()

    def close(self):
        self.cur.close()
        self.conn.close()
