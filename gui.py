import tkinter as tk
from tkinter import messagebox, ttk
from login import check_login
from server import DBConnection
from PIL import Image, ImageTk
from datetime import datetime, date
from funktionen import neuen_kunden_einpflegen, kunden_bearbeiten_popup, kunden_info_anzeigen, vertrag_hinzufuegen_popup, open_versicherungssparten_view
from funktionen import open_abgelaufene_vertraege_view
import sys
import os

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


#  Design-Farben und Schriften
FARBE_HINTERGRUND = "#f4f6f8"
FARBE_BUTTON = "#1976d2"
FARBE_BUTTON_HOVER = "#0d47a1"
FARBE_TEXT = "#263238"
SCHRIFT_STANDARD = ("Segoe UI", 11)
SCHRIFT_FETT = ("Segoe UI", 11, "bold")

# Einheitlicher Button-Stil
def erzeuge_button(master, text, command):
    return tk.Button(
        master, text=text, command=command,
        bg=FARBE_BUTTON, fg="white",
        activebackground=FARBE_BUTTON_HOVER,
        activeforeground="white",
        font=SCHRIFT_FETT, relief="flat",
        padx=10, pady=5, cursor="hand2"
    )

#  Format: 2024-05-26 -> 26.05.2024
def format_datum(d):
    try:
        return datetime.strptime(d, "%Y-%m-%d").strftime("%d.%m.%Y")
    except:
        return d

#  Start der App mit Login-Fenster
def start_app():
    root = tk.Tk()
    root.geometry("1200x600")
    root.configure(bg=FARBE_HINTERGRUND)

    try:
        logo = Image.open(resource_path("Grafik.png"))
        logo = logo.resize((160, 100))
        logo_img = ImageTk.PhotoImage(logo)
        label_logo = tk.Label(root, image=logo_img, bg=FARBE_HINTERGRUND)
        label_logo.image = logo_img
        label_logo.pack(pady=(30, 10))
    except:
        tk.Label(root, text="Logo nicht gefunden", font=SCHRIFT_STANDARD, bg=FARBE_HINTERGRUND, fg="red").pack(pady=20)

    LoginApp(root)
    root.mainloop()

#  LoginMaske mit Eingabe & Loginprüfung
class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Login")

        self.username = tk.StringVar()
        self.password = tk.StringVar()

        login_frame = tk.Frame(root, bg=FARBE_HINTERGRUND)
        login_frame.pack(pady=20)

        tk.Label(login_frame, text="Benutzername", font=SCHRIFT_STANDARD, bg=FARBE_HINTERGRUND, fg=FARBE_TEXT).grid(row=0, column=0, padx=10, pady=5)
        tk.Entry(login_frame, textvariable=self.username).grid(row=0, column=1, pady=5)

        tk.Label(login_frame, text="Passwort", font=SCHRIFT_STANDARD, bg=FARBE_HINTERGRUND, fg=FARBE_TEXT).grid(row=1, column=0, padx=10, pady=5)
        tk.Entry(login_frame, textvariable=self.password, show="*").grid(row=1, column=1, pady=5)

        erzeuge_button(root, "Login", self.login).pack(pady=15)

    def login(self):
        user = self.username.get()
        pw = self.password.get()
        success, rolle = check_login(user, pw)
        if success:
            self.root.title("Lade Hauptmenü...")
            open_hauptmenue(self.root, user, rolle)
        else:
            messagebox.showerror("Fehlgeschlagen", "Login fehlgeschlagen!")

# Hauptmenü-Ansicht
def open_hauptmenue(root, benutzername, rolle):
    for widget in root.winfo_children():
        widget.destroy()

    root.title(f"Hauptmenü - {benutzername}")
    root.configure(bg=FARBE_HINTERGRUND)

    try:
        logo = Image.open(resource_path("Grafik.png"))
        logo = logo.resize((160, 100))
        logo_img = ImageTk.PhotoImage(logo)
        label_logo = tk.Label(root, image=logo_img, bg=FARBE_HINTERGRUND)
        label_logo.image = logo_img  # Referenz speichern!
        label_logo.pack(pady=(20, 10))
    except:
        tk.Label(root, text="Logo nicht gefunden", font=SCHRIFT_STANDARD, bg=FARBE_HINTERGRUND, fg="red").pack(pady=10)

    # Begrüßung
    tk.Label(
        root,
        text=f"Willkommen, {benutzername}",
        font=SCHRIFT_FETT,
        bg=FARBE_HINTERGRUND,
        fg=FARBE_TEXT
    ).pack(pady=10)

    # Buttons für Navigation
    erzeuge_button(root, "Kundendaten einsehen", lambda: open_kundendaten_view(root, benutzername, rolle)).pack(pady=5)
    erzeuge_button(root, "Versicherungssparten anzeigen", lambda: open_versicherungssparten_view(root, benutzername, rolle)).pack(pady=5)
    erzeuge_button(root, "Abgelaufene Verträge anzeigen", lambda: open_abgelaufene_vertraege_view(root, benutzername, rolle)).pack(pady=5)
    erzeuge_button(root, "Abmelden", lambda: (root.destroy(), start_app())).pack(pady=5)

#  Kundendaten-Ansicht
def open_kundendaten_view(root, benutzername, rolle):
    for widget in root.winfo_children():
        widget.destroy()

    root.title("Kundendaten verwalten")
    root.geometry("1420x720")
    root.configure(bg=FARBE_HINTERGRUND)

    tk.Label(
        root,
        text=f"Kundendaten von: {benutzername}",
        font=SCHRIFT_FETT,
        bg=FARBE_HINTERGRUND,
        fg=FARBE_TEXT
    ).pack(pady=10)

    # Filter
    filter_frame = tk.Frame(root, bg=FARBE_HINTERGRUND)
    filter_frame.pack(pady=5)

    tk.Label(filter_frame, text="Nach Versicherungsart filtern:", font=SCHRIFT_STANDARD, bg=FARBE_HINTERGRUND, fg=FARBE_TEXT).pack(side=tk.LEFT)
    filter_var = tk.StringVar()
    tk.Entry(filter_frame, textvariable=filter_var, width=20).pack(side=tk.LEFT, padx=5)

    # Tabelle
    spalten = (
        "ID", "Anrede", "Name", "Vorname", "Geburtsdatum", "Telefonnummer", "E-Mail", "Vers.-Art",
        "Abschlussdatum", "Vers.-Beginn", "Vers. Ende", "Preis (mtl.)"
    )
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

    # Daten laden
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

    # Neuer Kunde
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

    # Kunde bearbeiten
    def kunde_bearbeiten():
        auswahl = kunden_tabelle.selection()
        if not auswahl:
            messagebox.showwarning("Auswahl fehlt", "Bitte einen Kunden auswählen.")
            return
        kunde = kunden_tabelle.item(auswahl[0])["values"]
        kunden_bearbeiten_popup(root, kunde, lambda: lade_kundendaten(filter_var.get()))

    # Kunde doppelt geklickt → Details anzeigen
    def kundeninfo_anzeigen_event(event):
        item = kunden_tabelle.identify_row(event.y)
        if item:
            kunde = kunden_tabelle.item(item)["values"]
            kunden_info_anzeigen(root, kunde, lambda k: vertrag_hinzufuegen_popup(root, k))

    kunden_tabelle.bind("<Double-1>", kundeninfo_anzeigen_event)

    def zurueck():
        from gui import open_hauptmenue
        open_hauptmenue(root, benutzername, rolle)

    # Buttons unten
    button_frame = tk.Frame(root, bg=FARBE_HINTERGRUND)
    button_frame.pack(pady=10)

    erzeuge_button(button_frame, "Filtern", lambda: lade_kundendaten(filter_var.get())).grid(row=0, column=0, padx=5)
    erzeuge_button(button_frame, "Neuen Kunden einpflegen", neuer_kunde).grid(row=0, column=1, padx=5)
    erzeuge_button(button_frame, "Kundenanschrift bearbeiten", kunde_bearbeiten).grid(row=0, column=2, padx=5)
    erzeuge_button(button_frame, "Zurück zum Hauptmenü", zurueck).grid(row=0, column=3, padx=5)

    lade_kundendaten()
#  Abgelaufene Verträge anzeigen
def open_abgelaufene_vertraege_view(root, benutzername, rolle):
    from gui import open_hauptmenue

    for widget in root.winfo_children():
        widget.destroy()

    root.title("Abgelaufene Verträge anzeigen")
    root.geometry("1000x600")
    root.configure(bg=FARBE_HINTERGRUND)

    tk.Label(root, text="Abgelaufene Verträge", font=SCHRIFT_FETT, bg=FARBE_HINTERGRUND, fg=FARBE_TEXT).pack(pady=10)

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
            if isinstance(eintrag[4], (datetime, date)):
                eintrag[4] = eintrag[4].strftime("%d.%m.%Y")
            tabelle.insert("", "end", values=eintrag)

    # Vertrag löschen
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

    # Button-Leiste unten
    button_frame = tk.Frame(root, bg=FARBE_HINTERGRUND)
    button_frame.pack(pady=15)

    erzeuge_button(button_frame, "Vertrag löschen", vertrag_loeschen).pack(side=tk.LEFT, padx=10)
    erzeuge_button(button_frame, "Zurück zum Hauptmenü", lambda: open_hauptmenue(root, benutzername, rolle)).pack(side=tk.LEFT, padx=10)

    lade_daten()
