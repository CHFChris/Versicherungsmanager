import tkinter as tk
from tkinter import ttk, messagebox
from server import DBConnection
from datetime import datetime
from PIL import Image, ImageTk
import sys
import os

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)



#Neuen Kunden einpflegen
def neuen_kunden_einpflegen(root, benutzername, rolle, mitarbeiter_id, refresh_callback):
    win = tk.Toplevel(root)
    win.title("Neuen Kunden einpflegen")
    win.geometry("600x650")

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
        "Haftpflicht": 6.25,
        "Wohngebäude": 18.33,
        "Rechtsschutz": 22.76
    }

    labels = [
        "Anrede", "Vorname", "Nachname", "Geburtsdatum (TT.MM.JJJJ)", "Straße", "Hausnummer",
        "Ort", "E-Mail", "Telefon", "Versicherungsart", 
        "Abschlussdatum (TT.MM.JJJJ)", "Beginn (TT.MM.JJJJ)", 
        "Ende (TT.MM.JJJJ)"
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
            entries["Ort"] = (cb, [o[0] for o in orte])
        elif label == "Versicherungsart":
            cb = ttk.Combobox(win, values=[s[1] for s in sparten], state="readonly")
            cb.grid(row=i, column=1, padx=5, pady=3)
            entries["Sparte"] = (cb, [s[0] for s in sparten])
        else:
            entry = tk.Entry(win)
            entry.grid(row=i, column=1, padx=5, pady=3)
            entries[label] = entry

#Datum auf TT.MM.YYYY geändert
    def parse_datum(d):
        return datetime.strptime(d.strip(), "%d.%m.%Y").strftime("%Y-%m-%d")

#Button der die Daten auf die Datenbank speichert
    def speichern():
        try:
            name = entries["Nachname"].get().strip()
            vorname = entries["Vorname"].get().strip()
            geb = parse_datum(entries["Geburtsdatum (TT.MM.JJJJ)"].get())
            strasse = entries["Straße"].get().strip()
            hausnr = entries["Hausnummer"].get().strip()
            ort_index = entries["Ort"][0].current()
            ort_id = entries["Ort"][1][ort_index]
            anrede_text = entries["Anrede"].get()
            anrede_id = {"Herr": 1, "Frau": 2, "Divers": 3}[anrede_text]
            email = entries["E-Mail"].get().strip()
            telefon = entries["Telefon"].get().strip()
            sparte_index = entries["Sparte"][0].current()
            sparte_id = entries["Sparte"][1][sparte_index]
            sparte_name = entries["Sparte"][0].get()
            preis = sparten_preise.get(sparte_name, 0.0)
            abschluss = parse_datum(entries["Abschlussdatum (TT.MM.JJJJ)"].get())
            beginn = parse_datum(entries["Beginn (TT.MM.JJJJ)"].get())
            ende = parse_datum(entries["Ende (TT.MM.JJJJ)"].get())

            db = DBConnection()
            cur = db.get_cursor()
            cur.execute("""
                INSERT INTO Kunde (Name, Vorname, Straße, Hausnummer, Ort_ID, Anrede, Geburtsdatum, Telefonnummer, `E-Mail`)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, vorname, strasse, hausnr, ort_id, anrede_id, geb, telefon, email))
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

    tk.Button(win, text="Speichern", command=speichern).grid(row=len(labels), column=0, columnspan=2, pady=10)

#Kunde bearbeiten Popup fenster
def kunden_bearbeiten_popup(root, kunde, refresh_callback):
    kunden_id = kunde[0]

    db = DBConnection()
    cur = db.get_cursor()
    cur.execute("""
        SELECT Name, Telefonnummer, `E-Mail`, Straße, Hausnummer, o.Ort_ID, o.Ort, o.PLZ
        FROM Kunde k
        JOIN Ort o ON k.Ort_ID = o.Ort_ID
        WHERE k.Kunden_ID = ?
    """, (kunden_id,))
    daten = cur.fetchone()

    cur.execute("SELECT Ort_ID, Ort, PLZ FROM Ort")
    orte = cur.fetchall()
    db.close()

    win = tk.Toplevel(root)
    win.title("Kundendaten bearbeiten")
    win.geometry("400x400")

    tk.Label(win, text="Nachname").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    name_entry = tk.Entry(win)
    name_entry.insert(0, daten[0])
    name_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(win, text="Telefon").grid(row=1, column=0, padx=5, pady=5, sticky="e")
    telefon_entry = tk.Entry(win)
    telefon_entry.insert(0, daten[1])
    telefon_entry.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(win, text="E-Mail").grid(row=2, column=0, padx=5, pady=5, sticky="e")
    email_entry = tk.Entry(win)
    email_entry.insert(0, daten[2])
    email_entry.grid(row=2, column=1, padx=5, pady=5)

    tk.Label(win, text="Straße").grid(row=3, column=0, padx=5, pady=5, sticky="e")
    strasse_entry = tk.Entry(win)
    strasse_entry.insert(0, daten[3])
    strasse_entry.grid(row=3, column=1, padx=5, pady=5)

    tk.Label(win, text="Hausnummer").grid(row=4, column=0, padx=5, pady=5, sticky="e")
    hausnummer_entry = tk.Entry(win)
    hausnummer_entry.insert(0, daten[4])
    hausnummer_entry.grid(row=4, column=1, padx=5, pady=5)

    tk.Label(win, text="Ort").grid(row=5, column=0, padx=5, pady=5, sticky="e")
    ort_cb = ttk.Combobox(win, values=[f"{o[1]} ({o[2]})" for o in orte], state="readonly")
    ort_cb.grid(row=5, column=1, padx=5, pady=5)
    ort_cb.set(f"{daten[6]} ({daten[7]})")
    ort_ids = [o[0] for o in orte]

#Kundendaten im Popup fenster (bearbeiten) speichern
    def speichern():
        try:
            ort_index = ort_cb.current()
            ort_id = ort_ids[ort_index]

            db = DBConnection()
            cur = db.get_cursor()
            cur.execute("""
                UPDATE Kunde
                SET Name = ?, Telefonnummer = ?, `E-Mail` = ?, Straße = ?, Hausnummer = ?, Ort_ID = ?
                WHERE Kunden_ID = ?
            """, (
                name_entry.get().strip(),
                telefon_entry.get().strip(),
                email_entry.get().strip(),
                strasse_entry.get().strip(),
                hausnummer_entry.get().strip(),
                ort_id,
                kunden_id
            ))
            db.commit()
            db.close()
            messagebox.showinfo("Erfolg", "Kundendaten wurden aktualisiert.")
            win.destroy()
            refresh_callback()
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Speichern: {e}")

    tk.Button(win, text="Speichern", command=speichern).grid(row=6, column=0, columnspan=2, pady=15)

#Kundeninfo anzeigen auf doppelclick
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

#Kundenvertrag hinzufügen mit den vorherigen Daten vom Kunden
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

#Datum auf TT.MM.YYYY anzeigen lassen
    def parse_datum(d):
        return datetime.strptime(d.strip(), "%d.%m.%Y").strftime("%Y-%m-%d")

#Vertrag speichern lassen
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
    from gui import open_hauptmenue
    import os

    for widget in root.winfo_children():
        widget.destroy()

    root.title("Versicherungssparten")
    root.geometry("1200x700")
    root.configure(bg="#f4f6f8")

    # Canvas und Scrollbar einrichten
    canvas = tk.Canvas(root, bg="#f4f6f8", highlightthickness=0)
    scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas, bg="#f4f6f8")

    canvas.create_window((0, 0), window=scroll_frame, anchor="nw", tags="all")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Scrollregion anpassen bei Änderungen
    scroll_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    # Zoom-Tracking-Variable
    zoom_level = {'scale': 1.0}

    def _on_mousewheel(event):
        if not canvas.winfo_exists():
            return  # vermeidet Absturz, wenn canvas nicht mehr existiert

        if event.state & 0x0004:  # STRG gedrückt
            factor = 1.1 if event.delta > 0 else 0.9
            canvas.scale("all", 0, 0, factor, factor)
            canvas.configure(scrollregion=canvas.bbox("all"))
        else:
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind("<MouseWheel>", _on_mousewheel)



    tk.Label(scroll_frame, text="Versicherungssparten", font=("Segoe UI", 14, "bold"),
             bg="#f4f6f8", fg="#263238").pack(pady=10)

    sparten_infos = [
        {
            "titel": "KFZ-Haftpflichtversicherung",
            "beschreibung": """(ist in Deutschland eine Pflichtversicherung).
Übernimmt Schäden an Dritte z.\u202fB. Personen-, Sach- und Vermögensschäden.
Teilkasko: Feuer, Hagel, Diebstahl, Marderbiss etc.
Vollkasko: inkl. Eigenschäden und Vandalismus.""",
            "preis": "102,75 €",
            "bild": "KFZ.png"
        },
        {
            "titel": "Hausratversicherung",
            "beschreibung": """Versichert Möbel, Schmuck, Bargeld (bis 1.500\u202f€).
Schutz bei Einbruch, Raub, Wasser- und Feuerschäden.""",
            "preis": "12,67 €",
            "bild": "Hausrat.png"
        },
        {
            "titel": "Wohngebäudeversicherung",
            "beschreibung": """Deckt Schäden am Haus durch Sturm, Feuer, Leitungswasser,
sowie optionale Elementargefahren.""",
            "preis": "18,33 €",
            "bild": "Wohngebäude.png"
        },
        {
            "titel": "Rechtsschutzversicherung",
            "beschreibung": """\u00dcbernimmt Anwalts- und Gerichtskosten bei Streitigkeiten –
privat, verkehrsrechtlich oder mietrechtlich.""",
            "preis": "22,76 €",
            "bild": "Rechtsschutz.png"
        },
        {
            "titel": "Privathaftpflichtversicherung",
            "beschreibung": """Zahlt bei versehentlich verursachten Schäden an Dritten.
Oft inkl. Schlüsselverlust.""",
            "preis": "6,25 €",
            "bild": "Privathaftpflicht.png"
        }
    ]

    bilder_refs = {}

    for eintrag in sparten_infos:
        frame = tk.Frame(scroll_frame, bg="white", bd=1, relief="solid")
        frame.pack(fill="x", padx=20, pady=10, ipady=10)

        inhalt = tk.Frame(frame, bg="white")
        inhalt.pack(fill="both", expand=True, padx=20, pady=15)

        text = tk.Frame(inhalt, bg="white")
        text.pack(side="left", fill="both", expand=True)

        tk.Label(text, text=eintrag["titel"], font=("Segoe UI", 11, "bold"),
                 bg="white", anchor="w").pack(anchor="w")
        tk.Label(text, text=eintrag["beschreibung"], font=("Segoe UI", 10),
                 bg="white", anchor="w", justify="left", wraplength=700).pack(anchor="w", pady=5)
        tk.Label(text, text=f"Preis: {eintrag['preis']} monatlich.",
                 font=("Segoe UI", 10, "bold"), fg="green", bg="white").pack(anchor="w")

        try:
            pfad = resource_path(eintrag["bild"])
            bild = Image.open(pfad).resize((250, 250), Image.LANCZOS)
            bildtk = ImageTk.PhotoImage(bild)
            label = tk.Label(inhalt, image=bildtk, bg="white")
            label.image = bildtk
            label.pack(side="right", padx=10)
        except Exception as e:
            print(f"Fehler beim Laden von {eintrag['bild']}: {e}")
            tk.Label(inhalt, text="Bild nicht gefunden", bg="white", fg="red").pack(side="right", padx=10)

    tk.Button(
        scroll_frame,
        text="Zurück zum Hauptmenü",
        command=lambda: open_hauptmenue(root, benutzername, rolle),
        bg="#1976d2",
        fg="white",
        font=("Segoe UI", 11, "bold"),
        activebackground="#0d47a1",
        activeforeground="white",
        relief="flat",
        padx=10,
        pady=5,
        cursor="hand2"
    ).pack(pady=20)



#Abgelaufene Verträge anzeigen lassen
def open_abgelaufene_vertraege_view(root, benutzername, rolle):
    from gui import open_hauptmenue
    for widget in root.winfo_children():
        widget.destroy()

    root.title("Abgelaufene Verträge anzeigen")
    root.geometry("1000x600")

    tk.Label(root, text="Abgelaufene Verträge", font=("Arial", 14)).pack(pady=10)

    spalten = ("Vertrags_ID", "Name", "Vorname", "Versicherungsart", "Versicherungsende")
    tabelle = ttk.Treeview(root, columns=spalten, show="headings")

    for col in spalten:
        tabelle.heading(col, text=col)
        tabelle.column(col, width=180, anchor="w")

    tabelle.pack(expand=True, fill="both", padx=20, pady=10)

#Datenladen der Abgelaufenen Verträge
    def lade_daten():
        heute = datetime.today().strftime("%Y-%m-%d")
        db = DBConnection()
        cur = db.get_cursor()

        if rolle == 2:  # Mitarbeitersicht
            query = """
                SELECT v.Vertrags_ID, k.Name, k.Vorname, s.Sparten, v.Versicherungsende
                FROM Vertraege v
                JOIN Kunde k ON v.Kunden_ID = k.Kunden_ID
                JOIN Versicherungssparte s ON v.Sparten_ID = s.Sparten_ID
                JOIN Benutzer b ON v.Mitarbeiter = b.Mitarbeiter_ID
                WHERE v.Versicherungsende < ? AND b.Benutzername = ?
            """
            cur.execute(query, (heute, benutzername))
        else:  # Adminsicht
            query = """
                SELECT v.Vertrags_ID, k.Name, k.Vorname, s.Sparten, v.Versicherungsende
                FROM Vertraege v
                JOIN Kunde k ON v.Kunden_ID = k.Kunden_ID
                JOIN Versicherungssparte s ON v.Sparten_ID = s.Sparten_ID
                WHERE v.Versicherungsende < ?
            """
            cur.execute(query, (heute,))

        daten = cur.fetchall()
        db.close()

        for row in tabelle.get_children():
            tabelle.delete(row)

        for eintrag in daten:
            eintrag = list(eintrag)
            eintrag[4] = datetime.strptime(eintrag[4], "%Y-%m-%d").strftime("%d.%m.%Y")
            tabelle.insert("", "end", values=eintrag)

#Vertrag aus der Tabelle löschen
    def vertrag_loeschen():
        auswahl = tabelle.selection()
        if not auswahl:
            messagebox.showwarning("Auswahl fehlt", "Bitte einen Vertrag auswählen.")
            return
        vertrag_id = tabelle.item(auswahl[0])["values"][0]

        if messagebox.askyesno("Löschen", "Möchten Sie diesen Vertrag wirklich löschen?"):
            db = DBConnection()
            cur = db.get_cursor()
            cur.execute("DELETE FROM Vertraege WHERE Vertrags_ID = ?", (vertrag_id,))
            db.commit()
            db.close()
            lade_daten()
            messagebox.showinfo("Erfolg", "Vertrag gelöscht.")

    button_frame = tk.Frame(root)
    button_frame.pack(pady=15)

    if rolle == 2:  # Mitarbeiter darf nur eigene löschen
        tk.Button(button_frame, text="Vertrag löschen", command=vertrag_loeschen).pack(side=tk.LEFT, padx=10)

    tk.Button(button_frame, text="Zurück zum Hauptmenü", command=lambda: open_hauptmenue(root, benutzername, rolle)).pack(side=tk.LEFT, padx=10)

    lade_daten()