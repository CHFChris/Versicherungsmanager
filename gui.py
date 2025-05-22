import tkinter as tk
from tkinter import messagebox, ttk
from login import check_login
from server import DBConnection
from PIL import Image, ImageTk
from datetime import datetime
from funktionen import neuen_kunden_einpflegen, kunden_bearbeiten_popup, kunden_info_anzeigen, vertrag_hinzufuegen_popup, open_versicherungssparten_view
from funktionen import open_abgelaufene_vertraege_view



def format_datum(d):
    try:
        return datetime.strptime(d, "%Y-%m-%d").strftime("%d.%m.%Y")
    except:
        return d

def open_kundendaten_view(root, benutzername, rolle):
    for widget in root.winfo_children():
        widget.destroy()

    root.title("Kundendaten verwalten")
    root.geometry("1200x600")
    tk.Label(root, text=f"Kundendaten von: {benutzername}", font=("Arial", 14)).pack(pady=10)

    filter_frame = tk.Frame(root)
    filter_frame.pack(pady=5)
    tk.Label(filter_frame, text="Nach Versicherungsart filtern:").pack(side=tk.LEFT)
    filter_var = tk.StringVar()
    tk.Entry(filter_frame, textvariable=filter_var, width=20).pack(side=tk.LEFT)

    spalten = ("ID", "Anrede", "Name", "Vorname", "Geburtsdatum", "Telefonnummer", "E-Mail", "Vers.-Art",
               "Abschlussdatum", "Vers.-Beginn", "Vers. Ende", "Preis (mtl.)")

    kunden_tabelle = ttk.Treeview(root, columns=spalten, show="headings")
    sortierstatus = {col: False for col in spalten}

    def sortiere_spalte(col):
        eintraege = [(kunden_tabelle.set(k, col), k) for k in kunden_tabelle.get_children("")]
        eintraege.sort(reverse=sortierstatus[col])
        for index, (val, k) in enumerate(eintraege):
            kunden_tabelle.move(k, '', index)
        sortierstatus[col] = not sortierstatus[col]

    for col in spalten:
        kunden_tabelle.heading(col, text=col, command=lambda _col=col: sortiere_spalte(_col))
        kunden_tabelle.column(col, width=110, stretch=True)

    kunden_tabelle.pack(expand=True, fill="both", padx=10, pady=5)

    def lade_kundendaten(filter_wert=""):
        db = DBConnection()
        cur = db.get_cursor()

        if rolle == 2:
            query = """
                SELECT k.Kunden_ID, a.Anrede, k.Name, k.Vorname, k.Geburtsdatum, k.Telefonnummer, k.`E-Mail`,
                       s.Sparten, v.Abschlussdatum, v.Versicherungsbeginn,
                       v.Versicherungsende, v.Versicherungspreis
                FROM Kunde k
                JOIN Anrede a ON k.Anrede = a.Anrede_ID
                JOIN Vertraege v ON k.Kunden_ID = v.Kunden_ID
                JOIN Benutzer b ON v.Mitarbeiter = b.Mitarbeiter_ID
                JOIN Versicherungssparte s ON v.Sparten_ID = s.Sparten_ID
                WHERE b.Benutzername = ?
            """
            params = [benutzername]
            if filter_wert:
                query += " AND s.Sparten LIKE ?"
                params.append(f"%{filter_wert}%")
        else:
            query = """
                SELECT k.Kunden_ID, a.Anrede, k.Name, k.Vorname, k.Geburtsdatum, k.Telefonnummer, k.`E-Mail`,
                       s.Sparten, v.Abschlussdatum, v.Versicherungsbeginn,
                       v.Versicherungsende, v.Versicherungspreis
                FROM Kunde k
                JOIN Anrede a ON k.Anrede = a.Anrede_ID
                JOIN Vertraege v ON k.Kunden_ID = v.Kunden_ID
                JOIN Versicherungssparte s ON v.Sparten_ID = s.Sparten_ID
            """
            params = []
            if filter_wert:
                query += " WHERE s.Sparten LIKE ?"
                params.append(f"%{filter_wert}%")

        cur.execute(query, tuple(params))
        daten = cur.fetchall()
        db.close()

        for row in kunden_tabelle.get_children():
            kunden_tabelle.delete(row)

        for eintrag in daten:
            eintrag = list(eintrag)
            eintrag[4] = format_datum(eintrag[4])
            eintrag[8] = format_datum(eintrag[8])
            eintrag[9] = format_datum(eintrag[9])
            eintrag[10] = format_datum(eintrag[10])
            eintrag[11] = f"{eintrag[11]:.2f} €".replace('.', ',')
            kunden_tabelle.insert("", tk.END, values=eintrag)

    def neuer_kunde():
        try:
            db = DBConnection()
            cur = db.get_cursor()
            cur.execute("SELECT Mitarbeiter_ID FROM Benutzer WHERE Benutzername = ?", (benutzername,))
            row = cur.fetchone()
            db.close()
            if row:
                mitarbeiter_id = row[0]
                neuen_kunden_einpflegen(root, benutzername, rolle, mitarbeiter_id, lambda: lade_kundendaten(filter_var.get()))
            else:
                messagebox.showerror("Fehler", "Mitarbeiter-ID nicht gefunden!")
        except Exception as e:
            messagebox.showerror("Fehler", f"Konnte Mitarbeiter-ID nicht ermitteln:\n{e}")

    def kunde_bearbeiten():
        auswahl = kunden_tabelle.selection()
        if not auswahl:
            messagebox.showwarning("Auswahl fehlt", "Bitte einen Kunden auswählen.")
            return
        kunde = kunden_tabelle.item(auswahl[0])["values"]
        kunden_bearbeiten_popup(root, kunde, lambda: lade_kundendaten(filter_var.get()))

    def kundeninfo_anzeigen_event(event):
        item = kunden_tabelle.identify_row(event.y)
        if item:
            kunde = kunden_tabelle.item(item)["values"]
            kunden_info_anzeigen(root, kunde, lambda k: vertrag_hinzufuegen_popup(root, k))

    kunden_tabelle.bind("<Double-1>", kundeninfo_anzeigen_event)

    def zurueck():
        from gui import open_hauptmenue
        open_hauptmenue(root, benutzername, rolle)

    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)
    tk.Button(button_frame, text="Filtern", command=lambda: lade_kundendaten(filter_var.get())).grid(row=0, column=0, padx=5)
    tk.Button(button_frame, text="Neuen Kunden einpflegen", command=neuer_kunde).grid(row=0, column=1, padx=5)
    tk.Button(button_frame, text="Kundenanschrift bearbeiten", command=kunde_bearbeiten).grid(row=0, column=2, padx=5)
    tk.Button(button_frame, text="Zurück zum Hauptmenü", command=zurueck).grid(row=0, column=3, padx=5)

    lade_kundendaten()

def open_hauptmenue(root, benutzername, rolle):
    for widget in root.winfo_children():
        widget.destroy()

    root.title(f"Hauptmenü - {benutzername}")
    tk.Label(root, text=f"Willkommen, {benutzername}", font=("Arial", 14)).pack(pady=10)

    tk.Button(root, text="Kundendaten einsehen", command=lambda: open_kundendaten_view(root, benutzername, rolle), width=30).pack(pady=5)
    tk.Button(root, text="Versicherungssparten anzeigen", command=lambda: open_versicherungssparten_view(root, benutzername, rolle), width=30).pack(pady=5)
    tk.Button(root, text="Abgelaufene Verträge anzeigen", command=lambda: open_abgelaufene_vertraege_view(root, benutzername, rolle), width=30).pack(pady=5)
    tk.Button(root, text="Abmelden", command=lambda: (root.destroy(), start_app()), width=30).pack(pady=5)

def open_abgelaufene_vertraege_view(root, benutzername, rolle):
    from gui import open_hauptmenue
    from datetime import datetime, date

    for widget in root.winfo_children():
        widget.destroy()

    root.title("Abgelaufene Verträge anzeigen")
    root.geometry("1000x600")

    tk.Label(root, text="Abgelaufene Verträge", font=("Arial", 14)).pack(pady=10)

    spalten = ("Vertrag_ID", "Name", "Vorname", "Versicherungsart", "Versicherungsende")
    tabelle = ttk.Treeview(root, columns=spalten, show="headings")

    for col in spalten:
        tabelle.heading(col, text=col)
        tabelle.column(col, width=180, anchor="w")

    tabelle.pack(expand=True, fill="both", padx=20, pady=10)

    def lade_daten():
        heute = datetime.today().strftime("%Y-%m-%d")
        db = DBConnection()
        cur = db.get_cursor()

        if rolle == 2:
            query = """
                SELECT v.Vertrag_ID, k.Name, k.Vorname, s.Sparten, v.Versicherungsende
                FROM Vertraege v
                JOIN Kunde k ON v.Kunden_ID = k.Kunden_ID
                JOIN Versicherungssparte s ON v.Sparten_ID = s.Sparten_ID
                JOIN Benutzer b ON v.Mitarbeiter = b.Mitarbeiter_ID
                WHERE v.Versicherungsende < ? AND b.Benutzername = ?
            """
            cur.execute(query, (heute, benutzername))
        else:
            query = """
                SELECT v.Vertrag_ID, k.Name, k.Vorname, s.Sparten, v.Versicherungsende
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
            # FIX: Falls eintrag[4] bereits ein datetime.date ist → direkt formatieren
            if isinstance(eintrag[4], (datetime, date)):
                eintrag[4] = eintrag[4].strftime("%d.%m.%Y")
            tabelle.insert("", "end", values=eintrag)

    def vertrag_loeschen():
        auswahl = tabelle.selection()
        if not auswahl:
            messagebox.showwarning("Auswahl fehlt", "Bitte einen Vertrag auswählen.")
            return
        vertrag_id = tabelle.item(auswahl[0])["values"][0]

        if messagebox.askyesno("Löschen", "Möchten Sie diesen Vertrag wirklich löschen?"):
            db = DBConnection()
            cur = db.get_cursor()
            cur.execute("DELETE FROM Vertraege WHERE Vertrag_ID = ?", (vertrag_id,))
            db.commit()
            db.close()
            lade_daten()
            messagebox.showinfo("Erfolg", "Vertrag gelöscht.")

    button_frame = tk.Frame(root)
    button_frame.pack(pady=15)

    tk.Button(button_frame, text="Vertrag löschen", command=vertrag_loeschen).pack(side=tk.LEFT, padx=10)
    tk.Button(button_frame, text="Zurück zum Hauptmenü", command=lambda: open_hauptmenue(root, benutzername, rolle)).pack(side=tk.LEFT, padx=10)

    lade_daten()



class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Login")

        canvas = tk.Canvas(root, height=100)
        canvas.pack()
        try:
            logo = Image.open("Grafik.png")
            logo = logo.resize((120, 100))
            self.logo_img = ImageTk.PhotoImage(logo)
            canvas.create_image(300, 60, image=self.logo_img)
        except:
            canvas.create_text(350, 60, text="Logo nicht gefunden", font=("Arial", 12))

        self.username = tk.StringVar()
        self.password = tk.StringVar()

        login_frame = tk.Frame(root)
        login_frame.pack(pady=20)

        tk.Label(login_frame, text="Benutzername").grid(row=0, column=0, padx=10, pady=5)
        tk.Entry(login_frame, textvariable=self.username).grid(row=0, column=1, pady=5)

        tk.Label(login_frame, text="Passwort").grid(row=1, column=0, padx=10, pady=5)
        tk.Entry(login_frame, textvariable=self.password, show='*').grid(row=1, column=1, pady=5)

        tk.Button(root, text="Login", command=self.login, width=20).pack(pady=10)

    def login(self):
        user = self.username.get()
        pw = self.password.get()
        success, rolle = check_login(user, pw)
        if success:
            self.root.title("Lade Hauptmenü...")
            open_hauptmenue(self.root, user, rolle)
        else:
            messagebox.showerror("Fehlgeschlagen", "Login fehlgeschlagen!")

def start_app():
    root = tk.Tk()
    root.geometry("1200x600")
    LoginApp(root)
    root.mainloop()
