import mariadb

class DBConnection:
    def __init__(self):
        try:
            self.conn = mariadb.connect(
                user="team07",
                password="BBVV2",
                host="10.80.0.206",
                port=3306,
                database="team07"
            )
            self.cur = self.conn.cursor()
            print(" Verbindung zur Datenbank erfolgreich!")
        except mariadb.Error as e:
            print(f" Fehler bei der Verbindung: {e}")
            exit(1)

    def get_cursor(self):
        return self.cur

    def commit(self):
        self.conn.commit()

    def close(self):
        self.cur.close()
        self.conn.close()
