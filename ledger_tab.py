"""Tab 2: Ledger screen — Clean Minimalist redesign."""
import tkinter as tk
from decimal import Decimal
from tkinter import ttk

from constants import ZERO, balfmt, fmt, date_to_display
from style import (
    BG, BG_ALT, BG_PANEL, BORDER_STRONG, PRIMARY, TEXT_MUTED, WARNING_LIGHT,
    F_BOLD, F_SM, F_XS,
    SP2, SP3, SP4, SP6,
    ACCENT_HOVER, ACCENT_LIGHT,
)


class LedgerMixin:
    def build_ledger(self, nb):
        tab = ttk.Frame(nb, style="Panel.TFrame")
        nb.add(tab, text="▥  Ledger")

        # ─── Top Bar: Account Selector ────────────────────────────────
        top_bar = ttk.Frame(tab, style="Panel.TFrame", padding=(SP6, SP4), height=72)
        top_bar.pack(fill="x")
        top_bar.pack_propagate(False)

        ttk.Label(top_bar, text="Account:", style="Muted.TLabel",
                  font=("Segoe UI", 13), foreground=TEXT_MUTED,
                  background=BG_PANEL).pack(side="left", padx=(0, SP3))

        self.v_ledger_acct = tk.StringVar(value="All Accounts")
        self.cb_ledger_acct = ttk.Combobox(
            top_bar,
            textvariable=self.v_ledger_acct,
            state="disabled",  # Locked by default
            width=42,
            style="LedgerFilter.TCombobox",
        )
        self.cb_ledger_acct.pack(side="left", padx=(0, SP6))
        self.cb_ledger_acct.bind("<<ComboboxSelected>>", self.on_ledger_account_change)
        self.cb_ledger_acct.bind("<<ComboboxSelected>>", lambda e: e.widget.selection_clear(), add="+")

        # Lock/unlock on click: click to edit, click outside to lock
        def _unlock_ledger_dropdown():
            self.cb_ledger_acct.configure(state="normal")
            self.cb_ledger_acct.after(10, lambda: self.cb_ledger_acct.event_generate("<Down>"))
            self.cb_ledger_acct.focus_set()

        def _lock_ledger_dropdown(event=None):
            if str(self.cb_ledger_acct.cget("state")) == "normal":
                self.cb_ledger_acct.configure(state="disabled")

        self.cb_ledger_acct.bind("<Button-1>", lambda e: (_lock_ledger_dropdown(), _unlock_ledger_dropdown())[1])
        top_bar.bind("<Button-1>", _lock_ledger_dropdown)
        self.cb_ledger_acct.bind("<FocusOut>", _lock_ledger_dropdown)

        # Thin separator between account selector and table (team version pattern)
        tk.Frame(tab, height=1, background=BORDER_STRONG, bd=0, highlightthickness=0).pack(fill="x")

        # ─── Ledger Table ────────────────────────────────────────────
        # Date | Explanation | Dr | Cr | Balance
        self.lt = self.make_tree(
            tab,
            ("date", "part", "dr", "cr", "bal"),
            ("Date", "Explanation", "Dr", "Cr", "Balance"),
            (140, 420, 130, 130, 150),
            left=("date", "part"),
        )
        self.lt.configure(style="Ledger.Treeview")

        self._configure_ledger_tags()

        # Prevent selection on empty state rows; clear selection on empty space click
        def _on_ledger_click(event):
            item = self.lt.identify_row(event.y)
            if not item:
                # Clicked on empty space — clear selection
                self.lt.selection_remove(self.lt.selection())
                return "break"
            if "empty" in self.lt.item(item, "tags"):
                # Clicked empty state row — prevent selection
                return "break"
            # Real row — allow normal selection

        self.lt.bind("<Button-1>", _on_ledger_click, add="+")

    def _configure_ledger_tags(self):
        """Ledger-specific tag configurations."""
        self.lt.tag_configure("adj", background=WARNING_LIGHT)
        self.lt.tag_configure("empty", background=BG, foreground=TEXT_MUTED, font=F_XS)
        self.lt.tag_configure("acct", background=ACCENT_LIGHT, font=F_BOLD, foreground=ACCENT_HOVER)

    def on_ledger_account_change(self, event):
        # event parameter is required by bind but not used
        _ = event
        self.refresh_ledger()

    def _compute_account_ledger(self, account_name):
        """Compute ledger data for a specific account. Returns (lines, balance, sum_debit, sum_credit)."""
        lines, bal, sd, sc = [], ZERO, ZERO, ZERO
        for e in sorted(self.entries, key=lambda x: x["date"]):
            a = Decimal(e["amount"])
            if e["debit"] == account_name:
                dr, cr, other = a, ZERO, e["credit"]
            elif e["credit"] == account_name:
                dr, cr, other = ZERO, a, e["debit"]
            else:
                continue
            bal += dr - cr
            sd += dr
            sc += cr
            part = (e["desc"] or other) + ("  [Adjusting Entry]" if e["adj"] else "")
            lines.append((date_to_display(e["date"]), part, fmt(dr), fmt(cr), balfmt(bal)))
        return lines, bal, sd, sc

    def refresh_ledger(self):
        if not hasattr(self, 'lt'):
            return
        self.lt.delete(*self.lt.get_children())

        selected = self.v_ledger_acct.get()
        accounts = self.get_all_account_names()

        if selected == "All Accounts":
            self._render_all_accounts(accounts)
        else:
            self._render_single_account(selected)

    def _render_all_accounts(self, accounts):
        """Render grouped ledger for all accounts with activity."""
        any_data = False

        for n in accounts:
            if n not in self.ledger_cache:
                self.ledger_cache[n] = self._compute_account_ledger(n)

            lines, bal, sd, sc = self.ledger_cache[n]

            if not lines:
                continue

            any_data = True

            # Account header row (group)
            header_iid = self.lt.insert(
                "", "end",
                values=("", n, "", "", ""),
                tags=("acct",),
                open=True
            )

            # Transaction rows
            for ln in lines:
                date_val, part_val, dr_val, cr_val, _ = ln
                is_adj = "[Adjusting Entry]" in part_val

                tags = ("adj",) if is_adj else ()
                self.lt.insert(
                    header_iid, "end",
                    values=(date_val, f"  {part_val}", dr_val, cr_val, ""),  # T-account format: balance only on Subtotal/TOTALS
                    tags=tags
                )

            # Subtotal row as child of header
            self.lt.insert(
                header_iid, "end",
                values=("", "  Subtotal", fmt(sd), fmt(sc), balfmt(bal)),
                tags=("total",)
            )

        if not any_data:
            self._render_empty_state("All Accounts")

    def _render_single_account(self, account_name):
        """Render ledger for a single account."""
        if account_name not in self.ledger_cache:
            self.ledger_cache[account_name] = self._compute_account_ledger(account_name)

        lines, bal, sd, sc = self.ledger_cache[account_name]

        if not lines:
            self._render_empty_state(account_name)
            return

        for ln in lines:
            date_val, part_val, dr_val, cr_val, _ = ln
            is_adj = "[Adjusting Entry]" in part_val

            tags = ("adj",) if is_adj else ()

            self.lt.insert("", "end", values=(date_val, part_val, dr_val, cr_val, ""), tags=tags)  # T-account format: balance only on TOTALS

        # Totals row
        self.lt.insert(
            "", "end",
            values=("", "TOTALS", fmt(sd), fmt(sc), balfmt(bal)),
            tags=("total",)
        )

    def _render_empty_state(self, account_name):
        """Render friendly empty state message."""
        self.lt.insert(
            "", "end",
            values=("", f"No transactions for {account_name} yet.", "", "", ""),
            tags=("empty",)
        )
        self.lt.insert(
            "", "end",
            values=("", "Add entries in the Journal tab", "", "", ""),
            tags=("empty",)
        )
