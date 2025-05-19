import tkinter as tk
from tkinter import ttk, messagebox
from server import DBConnection

def neuen_kunden_einpflegen(root, benutzername, rolle, mitarbeiter_id, refresh_callback):
    win = tk.Toplevel(root)
    win.title("Neuen Kunden einpflegen")
    win.geometry("400x500")

    labels = [
        "Name", "Vorname", "Geburtsdatum (YYYY-MM-DD)", "Straße", "Hausnummer",
        "Ort_ID", "Anrede_ID", "Sparte_ID", "Abschlussdatum (YYYY-MM-DD)",
        "Versicherungsbeginn (YYYY-MM-DD)", "Versicherungsende (YYYY-MM-DD)", "Versicherungspreis"
    ]

    entries = {}
    for i, label in enumerate(labels):
        tk.Label(win, text=label).grid(row=i, column=0, sticky="e", padx=5, pady=3)
        entry = tk.Entry(win, width=30)
        entry.grid(row=i, column=1, padx=5, pady=3)
        entries[label] = entry

    def speichern():
        try:
            daten = {k: v.get().strip() for k, v in entries.items()}
            if not all(daten.values()):
                raise ValueError("Alle Felder müssen ausgefüllt sein.")

            # Einfache Validierung
            float(daten["Versicherungspreis"])  # validiere Preis
            for feld in ["Geburtsdatum (YYYY-MM-DD)", "Abschlussdatum (YYYY-MM-DD)", 
                         "Versicherungsbeginn (YYYY-MM-DD)", "Versicherungsende (YYYY-MM-DD)"]:
                if len(daten[feld]) != 10 or daten[feld][4] != "-" or daten[feld][7] != "-":
                    raise ValueError(f"Ungültiges Datumsformat: {feld}")

            db = DBConnection()
            cur = db.get_cursor()

            # Kunden anlegen
            cur.execute("""
                INSERT INTO kunde (Name, Vorname, Straße, Hausnummer, Ort_ID, Anrede, Geburtsdatum)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                daten["Name"], daten["Vorname"], daten["Straße"], daten["Hausnummer"],
                int(daten["Ort_ID"]), int(daten["Anrede_ID"]), daten["Geburtsdatum (YYYY-MM-DD)"]
            ))
            kunden_id = cur.lastrowid

            # Vertrag anlegen
            cur.execute("""
                INSERT INTO vertraege (Kunden_ID, Abschlussdatum, Versicherungsbeginn, Versicherungsende,
                                       Mitarbeiter, Sparten_ID, Versicherungspreis)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                kunden_id,
                daten["Abschlussdatum (YYYY-MM-DD)"],
                daten["Versicherungsbeginn (YYYY-MM-DD)"],
                daten["Versicherungsende (YYYY-MM-DD)"],
                mitarbeiter_id,
                int(daten["Sparte_ID"]),
                float(daten["Versicherungspreis"])
            ))

            db.commit()
            db.close()
            messagebox.showinfo("Erfolg", "Kunde erfolgreich eingepflegt.")
            win.destroy()
            refresh_callback()  # Tabelle neu laden
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Einpflegen:\n{e}")

    tk.Button(win, text="Speichern", command=speichern).grid(row=len(labels), column=0, columnspan=2, pady=10)
