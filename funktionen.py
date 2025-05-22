import tkinter as tk
from tkinter import ttk, messagebox
from server import DBConnection
from datetime import datetime


def neuen_kunden_einpflegen(root, benutzername, rolle, mitarbeiter_id, refresh_callback):
    # ... unverändert ...
    pass

def kunden_bearbeiten_popup(root, kunde, refresh_callback):
    # ... unverändert ...
    pass

def kunden_info_anzeigen(root, kunde, vertrag_callback):
    win = tk.Toplevel(root)
    win.title("Kundendetails anzeigen")
    win.geometry("500x500")

    labels = [
        "Kunden-ID", "Anrede", "Name", "Vorname", "Geburtsdatum", "Telefon", "E-Mail",
        "Versicherungsart", "Abschlussdatum", "Beginn", "Ende", "Preis"
    ]

    for i, label in enumerate(labels):
        tk.Label(win, text=label).grid(row=i, column=0, padx=5, pady=5, sticky="e")
        tk.Label(win, text=str(kunde[i]), relief="sunken", anchor="w", width=30).grid(row=i, column=1, padx=5, pady=5)

    def neuer_vertrag():
        win.destroy()
        vertrag_callback(kunde)

    tk.Button(win, text="Neuen Vertrag hinzufügen", command=neuer_vertrag).grid(row=len(labels), column=0, columnspan=2, pady=15)

def vertrag_hinzufuegen_popup(root, kunde):
    win = tk.Toplevel(root)
    win.title("Neuen Vertrag anlegen")
    win.geometry("400x300")

    kunden_id = kunde[0]

    db = DBConnection()
    cur = db.get_cursor()
    cur.execute("SELECT Sparten_ID, Sparten FROM Versicherungssparte")
    sparten = cur.fetchall()
    db.close()

    sparten_preise = {
        "KFZ": 102.75,
        "Hausrat": 12.67,
        "Haftpflicht": 6.25,
        "Wohngebäude": 18.33,
        "Rechtsschutz": 22.76
    }

    tk.Label(win, text="Versicherungsart").grid(row=0, column=0, sticky="e", padx=5, pady=5)
    sparte_cb = ttk.Combobox(win, values=[s[1] for s in sparten], state="readonly")
    sparte_cb.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(win, text="Abschlussdatum (TT.MM.JJJJ)").grid(row=1, column=0, sticky="e", padx=5, pady=5)
    abschluss_entry = tk.Entry(win)
    abschluss_entry.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(win, text="Beginn (TT.MM.JJJJ)").grid(row=2, column=0, sticky="e", padx=5, pady=5)
    beginn_entry = tk.Entry(win)
    beginn_entry.grid(row=2, column=1, padx=5, pady=5)

    tk.Label(win, text="Ende (TT.MM.JJJJ)").grid(row=3, column=0, sticky="e", padx=5, pady=5)
    ende_entry = tk.Entry(win)
    ende_entry.grid(row=3, column=1, padx=5, pady=5)

    def parse_datum(d):
        return datetime.strptime(d.strip(), "%d.%m.%Y").strftime("%Y-%m-%d")

    def speichern():
        try:
            sparte_name = sparte_cb.get()
            sparte_id = next((s[0] for s in sparten if s[1] == sparte_name), None)
            preis = sparten_preise.get(sparte_name, 0.0)

            abschluss = parse_datum(abschluss_entry.get())
            beginn = parse_datum(beginn_entry.get())
            ende = parse_datum(ende_entry.get())

            db = DBConnection()
            cur = db.get_cursor()
            cur.execute("""
                INSERT INTO Vertraege (Kunden_ID, Abschlussdatum, Versicherungsbeginn, Versicherungsende, Mitarbeiter, Sparten_ID, Versicherungspreis)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (kunden_id, abschluss, beginn, ende, 1, sparte_id, preis))
            db.commit()
            db.close()

            messagebox.showinfo("Erfolg", "Vertrag erfolgreich hinzugefügt.")
            win.destroy()
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Speichern: {e}")

    tk.Button(win, text="Speichern", command=speichern).grid(row=4, column=0, columnspan=2, pady=10)

def open_versicherungssparten_view(root, benutzername, rolle):
    from gui import open_hauptmenue  # ✅ Lokaler Import zur Vermeidung von circular import

    for widget in root.winfo_children():
        widget.destroy()

    root.title("Versicherungssparten")
    root.geometry("1000x700")

    infos = [
        ("KFZ-Haftpflichtversicherung", "(ist in Deutschland eine Pflichtversicherung).\nÜbernimmt Schäden an dritte z. B. Personen- Sach und Vermögensschäden).\n Teilkasko (Feuer, Sturm/Hagel, Diebstahl, Marderbiss, Glasschäden und Zusammenstöße mit Tierhaarwild).\n Vollkasko (beinhaltet alles was in der Teilkaskoversicherung versichert ist und dazu Eigenschäden und Schäden durch Vandalismus).", "102,75 € monatlich."),
        ("Hausratversicherung", "Versichert bewegliche Gegenstände wie Möbel, Schmuck, Bargeld (bis 1.500 €).\nDeckt Schäden durch Einbruch, Raub, Wasser und Feuer ab.", "12,67 € monatlich."),
        ("Wohngebäudeversicherung", "Schützt das Gebäude – Dach, Fassade, fest verbaute Teile –\nvor Sturm, Wasser, Feuer und weiteren Elementargefahren.", "18,33 € monatlich."),
        ("Rechtsschutzversicherung", "Deckt Anwalts- und Gerichtskosten im privaten, verkehrsrechtlichen oder mietrechtlichen Bereich.", "22,76 € monatlich."),
        ("Privathaftpflichtversicherung", "Deckt Schäden ab, die Sie versehentlich Dritten zufügen – z. B. beim Fahrradfahren.\nAuch Schlüsselverlust ist mitversichert.", "6,25 € monatlich.")
    ]

    for i, (titel, beschreibung, preis) in enumerate(infos):
        tk.Label(root, text=titel, font=("Arial", 12, "bold"), anchor="w").pack(fill="x", padx=20, pady=(10 if i == 0 else 5, 0))
        tk.Label(root, text=beschreibung, justify="left", anchor="w", wraplength=950).pack(fill="x", padx=40)
        tk.Label(root, text=f"Preis: {preis}", fg="green", anchor="w").pack(fill="x", padx=40, pady=(0, 10))
        ttk.Separator(root, orient="horizontal").pack(fill="x", padx=20, pady=(0, 10))

    tk.Button(root, text="Zurück", command=lambda: open_hauptmenue(root, benutzername, rolle)).pack(pady=20)

