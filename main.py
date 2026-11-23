"""
Accounting App: Journal -> Ledger -> 12-Column Worksheet
Run with:  python main.py      (built-in modules only, nothing to install)
Data saves automatically to accounting_data.json beside this file.

The app is split into files so teammates can work on different parts:
    constants.py      shared constants and fmt()/balfmt()
    data.py           load/save data, account list
    style.py          look and feel, shared table builder
    journal_tab.py    Tab 1: Journal Entry
    ledger_tab.py     Tab 2: Ledger
    worksheet_tab.py  Tab 3: Worksheet / Balance Sheet
    about_tab.py      About dialog (from Help menu)
"""
import tkinter as tk
from tkinter import ttk

from about_tab import show_about
from data import DataMixin
from journal_tab import JournalMixin
from ledger_tab import LedgerMixin
from style import StyleMixin
from worksheet_tab import WorksheetMixin

import os
import sys

def resource_path(name):
    """Find a bundled file both when running the .py and when running the packaged .exe."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, name)


class App(DataMixin, StyleMixin, JournalMixin, LedgerMixin, WorksheetMixin):
    def __init__(self, root):
        self.root = root
        root.title("Accounting App")
        root.geometry("1280x760")
        root.minsize(1000, 600)
        # Set root background to match Panel.TFrame for seamless look (like team version)
        from style import BG_PANEL
        root.configure(background=BG_PANEL)
        # Start maximized on Windows
        try:
            root.state('zoomed')
        except tk.TclError:
            pass  # Not on Windows, ignore

        # --- Menu Bar ---
        menubar = tk.Menu(root)
        root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        export_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Export", menu=export_menu)
        export_menu.add_command(label="Export CSV", command=self.export_csv)
        export_menu.add_command(label="Export Excel", command=self.export_excel)
        export_menu.add_command(label="Export PDF", command=self.export_pdf)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=root.quit)

        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="New Entry\tCtrl+N", command=self.focus_new_entry)
        edit_menu.add_separator()
        edit_menu.add_command(label="Delete Entry\tDel", command=self.delete_selected_entry)

        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Refresh\tF5", command=self.refresh)

        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Validate Data", command=self.validate_data)
        tools_menu.add_command(label="Backup Manager...", command=self.show_backup_manager)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Keyboard Shortcuts", command=self.show_shortcuts)
        help_menu.add_separator()
        help_menu.add_command(label="About", command=lambda: show_about(root))

        self.entries, self.custom, self.ws_rows = [], {}, []
        self.ledger_cache = {}
        self.load()
        self.set_style()

        # Keyboard shortcut for F5 (Refresh)
        root.bind("<F5>", lambda e: self.refresh())

        # --- 3-tab notebook (Journal, Ledger, Worksheet) ---
        self.nb = ttk.Notebook(root)
        self.nb.pack(fill="both", expand=True, padx=10, pady=10)
        self.build_journal(self.nb)
        self.build_ledger(self.nb)
        self.build_worksheet(self.nb)
        self.refresh()

    # ---------- refresh everything ----------
    def refresh(self):
        names = self.all_account_names()

        # Update journal comboboxes (created in build_journal)
        if hasattr(self, 'cb_dr'):
            self.cb_dr["values"] = names
        if hasattr(self, 'cb_cr'):
            self.cb_cr["values"] = names

        # Update ledger dropdown (created in build_ledger)
        if hasattr(self, 'cb_ledger_acct') and hasattr(self, 'v_ledger_acct'):
            ledger_names = ["All Accounts"] + names
            self.cb_ledger_acct["values"] = ledger_names

            # Keep current selection if it still exists, otherwise fall back to "All Accounts"
            current = self.v_ledger_acct.get()
            if current not in ledger_names:
                self.v_ledger_acct.set("All Accounts")

        # Invalidate ledger cache since data changed
        self.ledger_cache.clear()

        # Refresh all tabs (they check for their own widgets)
        if hasattr(self, 'refresh_journal'):
            self.refresh_journal()
        if hasattr(self, 'refresh_ledger'):
            self.refresh_ledger()
        if hasattr(self, 'refresh_worksheet'):
            self.refresh_worksheet()

        # Clear journal entry form (View > Refresh should clear input boxes)
        self.clear_journal_form()

    def clear_journal_form(self):
        """Clear all journal entry form fields."""
        from datetime import date
        today = date.today()
        if hasattr(self, 'v_month'):
            self.v_month.set(today.strftime("%b"))
        if hasattr(self, 'v_day'):
            self.v_day.set(str(today.day))
        if hasattr(self, 'v_year'):
            self.v_year.set(str(today.year))
        if hasattr(self, 'v_dr'):
            self.v_dr.set("")
        if hasattr(self, 'v_cr'):
            self.v_cr.set("")
        if hasattr(self, 'v_amt'):
            self.v_amt.set("")
        if hasattr(self, 'v_desc'):
            self.v_desc.set("")
        if hasattr(self, 'v_adj'):
            self.v_adj.set(False)
        if hasattr(self, '_editing_index'):
            self._editing_index = None
        if hasattr(self, 'add_btn'):
            self.add_btn.configure(text="＋  Add Entry")
        if hasattr(self, 'cancel_btn'):
            self.cancel_btn.pack_forget()
        if hasattr(self, 'delete_btn'):
            self.delete_btn.pack_forget()
        if hasattr(self, 'status_var'):
            self.status_var.set("")
        # Lock all fields
        if hasattr(self, 'cb_month'):
            self.cb_month.configure(state="disabled")
        if hasattr(self, 'cb_day'):
            self.cb_day.configure(state="disabled")
        if hasattr(self, 'cb_year'):
            self.cb_year.configure(state="disabled")
        if hasattr(self, 'cb_dr'):
            self.cb_dr.configure(state="disabled")
        if hasattr(self, 'cb_cr'):
            self.cb_cr.configure(state="disabled")
        if hasattr(self, 'e_amt'):
            self.e_amt.configure(state="readonly")
        if hasattr(self, 'e_desc'):
            self.e_desc.configure(state="readonly")

    # ---------- Menu Actions ----------
    def focus_new_entry(self):
        """Focus the debit account field for new entry."""
        if hasattr(self, 'cb_dr'):
            self.nb.select(0)  # Switch to Journal tab
            self.cb_dr.focus_set()
            # Unlock the field
            if str(self.cb_dr.cget("state")) == "disabled":
                self.cb_dr.configure(state="normal")
                self.cb_dr.after(10, lambda: self.cb_dr.event_generate("<Down>"))

    def export_csv(self):
        """Export current view to CSV."""
        current_tab = self.nb.index(self.nb.select())
        if current_tab == 0:  # Journal
            self.export_journal_csv()
        elif current_tab == 1:  # Ledger
            self.export_ledger_csv()
        elif current_tab == 2:  # Worksheet
            self.export_worksheet_csv()

    def export_journal_csv(self):
        from tkinter import filedialog, messagebox
        import csv
        from constants import date_to_display
        path = filedialog.asksaveasfilename(defaultextension=".csv", initialfile="journal.csv",
                                            filetypes=[("CSV file", "*.csv")])
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(["Date", "Debit Account", "Credit Account", "Amount", "Description", "Adjusting"])
            for e in self.entries:
                w.writerow([date_to_display(e["date"]), e["debit"], e["credit"], e["amount"],
                           e.get("desc", ""), "Yes" if e.get("adj", False) else "No"])
        messagebox.showinfo("Export", "Journal exported to CSV.")

    def export_ledger_csv(self):
        from tkinter import filedialog, messagebox
        import csv
        from constants import date_to_display, fmt
        from decimal import Decimal
        path = filedialog.asksaveasfilename(defaultextension=".csv", initialfile="ledger.csv",
                                            filetypes=[("CSV file", "*.csv")])
        if not path:
            return
        selected = self.v_ledger_acct.get()
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(["Account", "Date", "Particulars", "Dr", "Cr", "Balance"])
            if selected == "All Accounts":
                for n in self.all_account_names():
                    if n not in self.ledger_cache:
                        self.ledger_cache[n] = self._compute_account_ledger(n)
                    lines, bal, sd, sc = self.ledger_cache[n]
                    if not lines:
                        continue
                    w.writerow([n, "", "", "", "", ""])
                    for ln in lines:
                        w.writerow(["", *ln])
                    w.writerow(["", "", "Subtotal", fmt(sd), fmt(sc), fmt(bal)])
            else:
                if selected not in self.ledger_cache:
                    self.ledger_cache[selected] = self._compute_account_ledger(selected)
                lines, bal, sd, sc = self.ledger_cache[selected]
                for ln in lines:
                    w.writerow([selected, *ln])
                w.writerow(["", "", "TOTALS", fmt(sd), fmt(sc), fmt(bal)])
        messagebox.showinfo("Export", "Ledger exported to CSV.")

    def delete_selected_entry(self):
        """Delete selected entry from current tab."""
        current_tab = self.nb.index(self.nb.select())
        if current_tab == 0:
            self.delete_entry()
        else:
            from tkinter import messagebox
            messagebox.showinfo("Delete Entry", "Select an entry in the Journal tab before deleting it.")

    def validate_data(self):
        from tkinter import messagebox
        issues = []
        for i, e in enumerate(self.entries):
            if not e.get("debit") or not e.get("credit"):
                issues.append(f"Entry {i+1}: Missing account")
            if e.get("debit") == e.get("credit"):
                issues.append(f"Entry {i+1}: Debit = Credit")
            try:
                from decimal import Decimal
                amt = Decimal(e["amount"])
                if amt <= 0:
                    issues.append(f"Entry {i+1}: Invalid amount")
            except:
                issues.append(f"Entry {i+1}: Invalid amount format")
        if issues:
            messagebox.showwarning("Validation Issues", "\n".join(issues))
        else:
            messagebox.showinfo("Validation", "All entries valid.")

    def show_backup_manager(self):
        from tkinter import messagebox
        import os
        from constants import DATA_FILE
        backup_dir = os.path.dirname(DATA_FILE)
        backups = [f for f in os.listdir(backup_dir) if f.startswith("accounting_data.backup.")]
        backups.sort(reverse=True)
        if backups:
            msg = f"Found {len(backups)} backup(s):\n\n" + "\n".join(backups[:10])
            if len(backups) > 10:
                msg += f"\n... and {len(backups) - 10} more"
        else:
            msg = "No backups found."
        messagebox.showinfo("Backup Manager", msg)

    def show_shortcuts(self):
        from tkinter import messagebox
        shortcuts = (
            "Keyboard Shortcuts:\n\n"
            "Ctrl+N     - New Entry (focus debit account)\n"
            "Ctrl+F     - Search (Journal tab)\n"
            "Del        - Delete selected entry\n"
            "F5         - Refresh\n"
            "Enter      - Submit form (when editing)\n"
            "Escape     - Close dialogs\n"
            "Tab        - Navigate fields\n"
            "Click      - Unlock field for editing\n"
            "Click outside - Lock all fields\n"
            "\nNote: Data saves automatically on every change."
        )
        messagebox.showinfo("Keyboard Shortcuts", shortcuts)


if __name__ == "__main__":
    root = tk.Tk()
    try:
        root.iconbitmap(resource_path("logo.ico"))
    except tk.TclError:
        pass  # icon file missing: keep the default icon
    App(root)
    root.mainloop()