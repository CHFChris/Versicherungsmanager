import tkinter as tk
from tkinter import messagebox, ttk
from login import check_login
from server import DBConnection
from PIL import Image, ImageTk
from datetime import datetime
from funktionen import neuen_kunden_einpflegen

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

    spalten = ("ID", "Name", "Vorname", "Telefonnummer", "E-Mail", "Geburtsdatum", "Versicherungsart",
               "Abschlussdatum", "Beginn", "Ende", "Preis (mtl.)")

    kunden_tabelle = ttk.Treeview(root, columns=spalten, show="headings")

    for col in spalten:
        kunden_tabelle.heading(col, text=col)
        kunden_tabelle.column(col, width=110, stretch=True)

    kunden_tabelle.pack(expand=True, fill="both", padx=10, pady=5)

    def lade_kundendaten(filter_wert=""):
        db = DBConnection()
        cur = db.get_cursor()

        if rolle == 2:
            query = """
                SELECT k.Kunden_ID, k.Name, k.Vorname, k.Telefonnummer, k.`E-Mail`, k.Geburtsdatum,
                       s.Sparten, v.Abschlussdatum, v.Versicherungsbeginn,
                       v.Versicherungsende, v.Versicherungspreis
                FROM Kunde k
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
                SELECT k.Kunden_ID, k.Name, k.Vorname, k.Telefonnummer, k.`E-Mail`, k.Geburtsdatum,
                       s.Sparten, v.Abschlussdatum, v.Versicherungsbeginn,
                       v.Versicherungsende, v.Versicherungspreis
                FROM Kunde k
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
            eintrag[5] = format_datum(eintrag[5])  # Geburtsdatum
            eintrag[7] = format_datum(eintrag[7])  # Abschlussdatum
            eintrag[8] = format_datum(eintrag[8])  # Beginn
            eintrag[9] = format_datum(eintrag[9])  # Ende
            eintrag[10] = f"{eintrag[10]:.2f} €".replace('.', ',')  # Preis
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

        edit_win = tk.Toplevel(root)
        edit_win.title("Kunden bearbeiten")
        edit_win.geometry("400x400")

        tk.Label(edit_win, text="Nachname").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        name_entry = tk.Entry(edit_win, width=30)
        name_entry.insert(0, daten[0])
        name_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(edit_win, text="Telefonnummer").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        telefon_entry = tk.Entry(edit_win, width=30)
        telefon_entry.insert(0, daten[1])
        telefon_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(edit_win, text="E-Mail").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        email_entry = tk.Entry(edit_win, width=30)
        email_entry.insert(0, daten[2])
        email_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(edit_win, text="Straße").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        strasse_entry = tk.Entry(edit_win, width=30)
        strasse_entry.insert(0, daten[3])
        strasse_entry.grid(row=3, column=1, padx=5, pady=5)

        tk.Label(edit_win, text="Hausnummer").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        hausnummer_entry = tk.Entry(edit_win, width=30)
        hausnummer_entry.insert(0, daten[4])
        hausnummer_entry.grid(row=4, column=1, padx=5, pady=5)

        tk.Label(edit_win, text="Ort").grid(row=5, column=0, padx=5, pady=5, sticky="e")
        ort_cb = ttk.Combobox(edit_win, values=[f"{o[1]} ({o[2]})" for o in orte], state="readonly", width=28)
        ort_cb.grid(row=5, column=1, padx=5, pady=5)
        ort_ids = [o[0] for o in orte]
        ort_cb.set(f"{daten[6]} ({daten[7]})")

        def speichern_aenderung():
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
                edit_win.destroy()
                lade_kundendaten(filter_var.get())
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Speichern:\n{e}")

        tk.Button(edit_win, text="Speichern", command=speichern_aenderung).grid(row=6, column=0, columnspan=2, pady=15)

    def kunde_loeschen():
        auswahl = kunden_tabelle.selection()
        if not auswahl:
            messagebox.showwarning("Auswahl fehlt", "Bitte einen Kunden auswählen.")
            return
        kunde = kunden_tabelle.item(auswahl[0])["values"]
        if rolle == 1:
            messagebox.showinfo("Löschen", f"Kunde ID {kunde[0]} wird gelöscht.")
        else:
            messagebox.showinfo("Löschen", f"Vertrag von Kunde ID {kunde[0]} wird geändert.")

    def zurueck():
        open_hauptmenue(root, benutzername, rolle)

    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)
    tk.Button(button_frame, text="Filtern", command=lambda: lade_kundendaten(filter_var.get())).grid(row=0, column=0, padx=5)
    tk.Button(button_frame, text="Neuen Kunden einpflegen", command=neuer_kunde).grid(row=0, column=1, padx=5)
    tk.Button(button_frame, text=("Kunden bearbeiten" if rolle == 1 else "Kundenanschrift bearbeiten"), command=kunde_bearbeiten).grid(row=0, column=2, padx=5)
    tk.Button(button_frame, text=("Kunden löschen" if rolle == 1 else "Kundenvertrag ändern"), command=kunde_loeschen).grid(row=0, column=3, padx=5)
    tk.Button(button_frame, text="Zurück zum Hauptmenü", command=zurueck).grid(row=0, column=4, padx=5)

    lade_kundendaten()

def open_hauptmenue(root, benutzername, rolle):
    for widget in root.winfo_children():
        widget.destroy()

    root.title(f"Hauptmenü - {benutzername}")
    tk.Label(root, text=f"Willkommen, {benutzername}", font=("Arial", 14)).pack(pady=10)

    tk.Button(root, text="Kundendaten einsehen", command=lambda: open_kundendaten_view(root, benutzername, rolle), width=30).pack(pady=5)
    tk.Button(root, text="Versicherungssparten anzeigen", command=lambda: messagebox.showinfo("Info", "Versicherungssparten"), width=30).pack(pady=5)
    tk.Button(root, text="Abgelaufene Verträge anzeigen", command=lambda: messagebox.showinfo("Info", "Abgelaufene Verträge"), width=30).pack(pady=5)
    tk.Button(root, text="Abmelden", command=lambda: (root.destroy(), start_app()), width=30).pack(pady=5)

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
