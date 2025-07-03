using MySql.Data.MySqlClient;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using MySql.Data.MySqlClient;
using System;
using System.Windows.Forms;

namespace MariaDB_20250703
{
    public partial class Form1 : Form
    {
        public Form1()
        {
            InitializeComponent();
        }

        private void bn_start_Click(object sender, EventArgs e)
        {
            string kundenname = tb_eingabe.Text.Trim();
            lib_ausgabe.Items.Clear();

            if (string.IsNullOrWhiteSpace(kundenname))
            {
                lib_ausgabe.Items.Add("Bitte einen Kundennamen eingeben.");
                return;
            }

            string connectionString = "server=10.80.0.206;port=3306;user=team07;password=BBVV2;database=team07";

            string query = @"   SELECT v.Vertrag_ID, k.Vorname, k.Name, s.Sparten, v.Versicherungsbeginn, v.Versicherungsende, v.Versicherungspreis
                                FROM Vertraege v
                                JOIN Kunde k ON v.Kunden_ID = k.Kunden_ID
                                JOIN Versicherungssparte s ON v.Sparten_ID = s.Sparten_ID
                                WHERE k.Name LIKE @Name
                                ORDER BY v.Versicherungsbeginn DESC";

            using (MySqlConnection conn = new MySqlConnection(connectionString))
            using (MySqlCommand cmd = new MySqlCommand(query, conn))
            {
                cmd.Parameters.AddWithValue("@Name", "%" + kundenname + "%");

                try
                {
                    conn.Open();
                    using (MySqlDataReader reader = cmd.ExecuteReader())
                    {
                        if (!reader.HasRows)
                        {
                            lib_ausgabe.Items.Add("Keine Verträge gefunden.");
                            return;
                        }

                        while (reader.Read())
                        {
                            string eintrag = $"Vertrag #{reader["Vertrag_ID"]}: {reader["Vorname"]} {reader["Name"]}, {reader["Sparten"]}, " +
                                             $"von {Convert.ToDateTime(reader["Versicherungsbeginn"]):dd.MM.yyyy} bis {Convert.ToDateTime(reader["Versicherungsende"]):dd.MM.yyyy}, " +
                                             $"{Convert.ToDecimal(reader["Versicherungspreis"]):0.00} €";
                            lib_ausgabe.Items.Add(eintrag);
                        }
                    }
                }
                catch (Exception ex)
                {
                    lib_ausgabe.Items.Add("Fehler: " + ex.Message);
                }
            }
        }

        private void tb_eingabe_TextChanged(object sender, EventArgs e)
        {

        }
    }
}
