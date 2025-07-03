namespace MariaDB_20250703
{
    partial class Form1
    {
        /// <summary>
        /// Erforderliche Designervariable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Verwendete Ressourcen bereinigen.
        /// </summary>
        /// <param name="disposing">True, wenn verwaltete Ressourcen gelöscht werden sollen; andernfalls False.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Vom Windows Form-Designer generierter Code

        /// <summary>
        /// Erforderliche Methode für die Designerunterstützung.
        /// Der Inhalt der Methode darf nicht mit dem Code-Editor geändert werden.
        /// </summary>
        private void InitializeComponent()
        {
            this.tb_eingabe = new System.Windows.Forms.TextBox();
            this.bn_start = new System.Windows.Forms.Button();
            this.lib_ausgabe = new System.Windows.Forms.ListBox();
            this.SuspendLayout();
            // 
            // tb_eingabe
            // 
            this.tb_eingabe.Location = new System.Drawing.Point(32, 59);
            this.tb_eingabe.Name = "tb_eingabe";
            this.tb_eingabe.Size = new System.Drawing.Size(133, 26);
            this.tb_eingabe.TabIndex = 0;
            this.tb_eingabe.TextChanged += new System.EventHandler(this.tb_eingabe_TextChanged);
            // 
            // bn_start
            // 
            this.bn_start.Location = new System.Drawing.Point(32, 103);
            this.bn_start.Name = "bn_start";
            this.bn_start.Size = new System.Drawing.Size(133, 33);
            this.bn_start.TabIndex = 1;
            this.bn_start.Text = "Start";
            this.bn_start.UseVisualStyleBackColor = true;
            this.bn_start.Click += new System.EventHandler(this.bn_start_Click);
            // 
            // lib_ausgabe
            // 
            this.lib_ausgabe.FormattingEnabled = true;
            this.lib_ausgabe.ItemHeight = 20;
            this.lib_ausgabe.Location = new System.Drawing.Point(32, 163);
            this.lib_ausgabe.Name = "lib_ausgabe";
            this.lib_ausgabe.Size = new System.Drawing.Size(723, 264);
            this.lib_ausgabe.TabIndex = 2;
            // 
            // Form1
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(9F, 20F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(800, 450);
            this.Controls.Add(this.lib_ausgabe);
            this.Controls.Add(this.bn_start);
            this.Controls.Add(this.tb_eingabe);
            this.Name = "Form1";
            this.Text = "Form1";
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.TextBox tb_eingabe;
        private System.Windows.Forms.Button bn_start;
        private System.Windows.Forms.ListBox lib_ausgabe;
    }
}

