import bcrypt
from server import DBConnection

def check_login(benutzername, passwort):
    db = DBConnection()
    cur = db.get_cursor()

    cur.execute("SELECT PasswortHash, Rolle_ID FROM Benutzer WHERE Benutzername = ?", (benutzername,))
    row = cur.fetchone()

    if row and bcrypt.checkpw(passwort.encode('utf-8'), row[0].encode('utf-8')):
        return True, row[1]
    return False, None
