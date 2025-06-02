import bcrypt
from server import DBConnection
from datetime import datetime

def check_login(benutzername, passwort):
    db = DBConnection()
    cur = db.get_cursor()

    # Benutzer anhand des Namens finden (case-sensitive)
    cur.execute("SELECT Benutzer_ID, PasswortHash, Rolle_ID FROM Benutzer WHERE Benutzername = ?", (benutzername,))
    row = cur.fetchone()

    erfolgreich = False
    benutzer_id = None
    rolle_id = None

    # Passwort überprüfen
    if row and bcrypt.checkpw(passwort.encode('utf-8'), row[1].encode('utf-8')):
        erfolgreich = True
        benutzer_id = row[0]
        rolle_id = row[2]

    # Loginversuch protokollieren in Tabelle `login`
    loginzeit = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cur.execute("INSERT INTO login (Benutzer_ID, Loginzeit, Erfolgreich) VALUES (?, ?, ?)",
                (benutzer_id, loginzeit, erfolgreich))

    db.commit()
    db.close()

    return erfolgreich, rolle_id if erfolgreich else None
