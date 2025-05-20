import bcrypt
from server import DBConnection

def check_login(benutzername, passwort):
    if benutzername != benutzername.capitalize():
        return False, None

    db = DBConnection()
    cur = db.get_cursor()

    # Case-sensitive Vergleich mit exakt eingegebenem Benutzernamen
    cur.execute("SELECT PasswortHash, Rolle_ID FROM Benutzer WHERE Benutzername = ?", (benutzername,))
    row = cur.fetchone()

    if row and bcrypt.checkpw(passwort.encode('utf-8'), row[0].encode('utf-8')):
        return True, row[1]
    return False, None
