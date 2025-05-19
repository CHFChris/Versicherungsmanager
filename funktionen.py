import tkinter as tk
from tkinter import ttk, messagebox
from server import DBConnection
from datetime import datetime

def neuen_kunden_einpflegen(root, benutzername, rolle, mitarbeiter_id, refresh_callback):
    win = tk.Toplevel(root)
    win.title("Neuen Kunden einpflegen")
    win.geometry("500x650")

    db = DBConnection()
    cur = db.get_cursor()

    cur.execute("SELECT Ort_ID, Ort, PLZ FROM Ort")
    orte = cur.fetchall()

    cur.execute("SELECT Sparten_ID, Sparten FROM Versicherungssparte")
    sparten = cur.fetchall()
    db.close()

    sparten_preise = {
        "KFZ": 102.75,
        "Hausrat": 12.67,
        "Haftpflicht":  6.25,
        "Wohngebäude": 18.33,
        "Rechtsschutz": 22.76
    }

    labels = [
        "Anrede", "Vorname", "Name", "Geburtsdatum (TT.MM.JJJJ)", "Straße", "Hausnummer",
        "Ort", "E-Mail", "Telefonnummer", "Versicherungsart", 
        "Abschlussdatum (TT.MM.JJJJ)", "Versicherungsbeginn (TT.MM.JJJJ)", 
        "Versicherungsende (TT.MM.JJJJ)", "Versicherungspreis"
    ]

    entries = {}

    for i, label in enumerate(labels):
        tk.Label(win, text=label).grid(row=i, column=0, sticky="e", padx=5, pady=3)

        if label == "Anrede":
            cb = ttk.Combobox(win, values=["Herr", "Frau", "Divers"], state="readonly")
            cb.grid(row=i, column=1, padx=5, pady=3)
            entries["Anrede"] = cb
        elif label == "Ort":
            cb = ttk.Combobox(win, values=[f"{o[1]} {o[2]}" for o in orte], state="readonly")
            cb.grid(row=i, column=1, padx=5, pady=3)
            entries["Ort_ID"] = (cb, [o[0] for o in orte])
        elif label == "Versicherungsart":
            cb = ttk.Combobox(win, values=[s[1] for s in sparten], state="readonly")
            cb.grid(row=i, column=1, padx=5, pady=3)
            entries["Sparte_ID"] = (cb, [s[0] for s in sparten])
        elif label == "Versicherungspreis":
            entry = tk.Entry(win, state="readonly")
            entry.grid(row=i, column=1, padx=5, pady=3)
            entries["Versicherungspreis"] = entry
        else:
            entry = tk.Entry(win, width=30)
            entry.grid(row=i, column=1, padx=5, pady=3)
            entries[label] = entry

    # Automatischer Preis bei Auswahl der Sparte
    def aktualisiere_preis(event):
        sparten_cb = entries["Sparte_ID"][0]
        aktuelle_sparte = sparten_cb.get()
        preisfeld = entries["Versicherungspreis"]
        preis = sparten_preise.get(aktuelle_sparte, 0.0)
        preisfeld.config(state="normal")
        preisfeld.delete(0, tk.END)
        preisfeld.insert(0, f"{preis:.2f}")
        preisfeld.config(state="readonly")

    entries["Sparte_ID"][0].bind("<<ComboboxSelected>>", aktualisiere_preis)

    def parse_datum(d, feldname):
        try:
            return datetime.strptime(d.strip(), "%d.%m.%Y").strftime("%Y-%m-%d")
        except:
            raise ValueError(f"Ungültiges Datum in '{feldname}' (TT.MM.JJJJ erwartet).")

    def speichern():
        try:
            name = entries["Name"].get().strip()
            vorname = entries["Vorname"].get().strip()
            geburtsdatum = parse_datum(entries["Geburtsdatum (TT.MM.JJJJ)"].get(), "Geburtsdatum")
            strasse = entries["Straße"].get().strip()
            hausnummer = entries["Hausnummer"].get().strip()
            email = entries["E-Mail"].get().strip()
            telefon = entries["Telefonnummer"].get().strip()

            ort_index = entries["Ort_ID"][0].current()
            ort_id = entries["Ort_ID"][1][ort_index]

            anrede_text = entries["Anrede"].get()
            anrede_id = {"Herr": 1, "Frau": 2, "Divers": 3}[anrede_text]

            sparte_index = entries["Sparte_ID"][0].current()
            sparte_id = entries["Sparte_ID"][1][sparte_index]
            preis = float(entries["Versicherungspreis"].get())

            abschluss = parse_datum(entries["Abschlussdatum (TT.MM.JJJJ)"].get(), "Abschlussdatum")
            beginn = parse_datum(entries["Versicherungsbeginn (TT.MM.JJJJ)"].get(), "Versicherungsbeginn")
            ende = parse_datum(entries["Versicherungsende (TT.MM.JJJJ)"].get(), "Versicherungsende")

            db = DBConnection()
            cur = db.get_cursor()

            cur.execute("""
                INSERT INTO Kunde (Name, Vorname, Straße, Hausnummer, Ort_ID, Anrede, Geburtsdatum, Telefonnummer, `E-Mail`)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, vorname, strasse, hausnummer, ort_id, anrede_id, geburtsdatum, telefon, email))
            kunden_id = cur.lastrowid

            cur.execute("""
                INSERT INTO Vertraege (Kunden_ID, Abschlussdatum, Versicherungsbeginn, Versicherungsende,
                                       Mitarbeiter, Sparten_ID, Versicherungspreis)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (kunden_id, abschluss, beginn, ende, mitarbeiter_id, sparte_id, preis))

            db.commit()
            db.close()
            messagebox.showinfo("Erfolg", "Kunde erfolgreich hinzugefügt.")
            win.destroy()
            refresh_callback()
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Speichern:\n{e}")

    tk.Button(win, text="Speichern", command=speichern).grid(row=len(labels), column=0, columnspan=2, pady=15)
