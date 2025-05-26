import bcrypt
from server import DBConnection

# Login prüfen (Case-Sensitive!)
def check_login(benutzername, passwort):
    db = DBConnection()
    cur = db.get_cursor()

    # Groß-/Kleinschreibung beachten (BINARY = case-sensitive Vergleich)
    cur.execute("SELECT PasswortHash, Rolle_ID FROM Benutzer WHERE BINARY Benutzername = ?", (benutzername,))
    row = cur.fetchone()

    if row:
        gespeicherter_hash = row[0]
        if isinstance(gespeicherter_hash, str):
            gespeicherter_hash = gespeicherter_hash.encode('utf-8')

        if bcrypt.checkpw(passwort.encode('utf-8'), gespeicherter_hash):
            return True, row[1]

    return False, None
