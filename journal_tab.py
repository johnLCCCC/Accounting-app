"""Tab 1: Journal Entry screen — Clean Minimalist redesign."""
import copy
import tkinter as tk
import calendar
import math
from datetime import date
from decimal import Decimal, InvalidOperation
from tkinter import font as tkfont, ttk, messagebox

from constants import ASSET, TYPES, date_to_display
from style import (
    BG_ALT, BG_PANEL, BORDER, BORDER_STRONG, PRIMARY, PRIMARY_HOVER, PRIMARY_FOCUS,
    TEXT, TEXT_INVERTED, TEXT_MUTED,
    COLOR_DANGER, COLOR_DANGER_LIGHT, COLOR_SUCCESS, COLOR_SUCCESS_LIGHT, COLOR_BG_PANEL,
    F_MONO,
    SP1, SP2, SP3, SP4, SP5, SP6,
    fmt_amt,
)
from journal_table import JournalTable


class JournalMixin:
    def build_journal(self, nb):
        tab = ttk.Frame(nb, style="Panel.TFrame")
        nb.add(tab, text="▤  Journal")

        # ─── Journal Entry Form Panel ──────────────────────────────────────────
        form_panel = ttk.Frame(tab, style="Panel.TFrame", padding=(SP6, SP5))
        form_panel.pack(fill="x", padx=SP6, pady=(SP6, SP4))

        # Row 0: Field labels
        labels = ["Date", "Debit Account", "Credit Account", "Amount", "Description"]
        # Use proportional weights for responsive layout
        weights = [10, 22, 22, 12, 34]
        for c, (label, w) in enumerate(zip(labels, weights)):
            ttk.Label(form_panel, text=label, style="FieldLabel.TLabel").grid(
                row=0, column=c, sticky="w", padx=(0, SP3)
            )
            form_panel.columnconfigure(c, weight=w)

        # Thin separator below form title (team version pattern)
        tk.Frame(tab, height=1, background=BORDER_STRONG, bd=0, highlightthickness=0).pack(fill="x", padx=SP6)

        # Row 1: Input fields
        self.v_dr = tk.StringVar()
        self.v_cr = tk.StringVar()
        self.v_amt = tk.StringVar()
        self.v_desc = tk.StringVar()
        self.v_adj = tk.BooleanVar()

        # Date: Month / Day / Year comboboxes
        today = date.today()
        self.v_month = tk.StringVar(value=today.strftime("%b"))
        self.v_day = tk.StringVar(value=str(today.day))
        self.v_year = tk.StringVar(value=str(today.year))

        # Month names for combobox
        self.month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

        # Year range for combobox (10 years back, 5 years forward)
        current_year = today.year
        self.year_values = [str(y) for y in range(current_year - 10, current_year + 6)]

        # Date frame to hold three comboboxes
        date_frame = ttk.Frame(form_panel, style="Panel.TFrame")
        date_frame.grid(row=1, column=0, sticky="ew", padx=(0, SP3), pady=(SP2, SP4))
        date_frame.columnconfigure(0, weight=1)
        date_frame.columnconfigure(1, weight=1)
        date_frame.columnconfigure(2, weight=1)

        self.cb_month = ttk.Combobox(date_frame, textvariable=self.v_month,
                                      values=self.month_names, width=5, state="disabled", justify="center")
        self.cb_day = ttk.Combobox(date_frame, textvariable=self.v_day,
                                    width=4, state="disabled", justify="center")
        self.cb_year = ttk.Combobox(date_frame, textvariable=self.v_year,
                                     values=self.year_values, width=6, state="disabled", justify="center")

        self.cb_month.grid(row=0, column=0, sticky="ew", padx=(0, 2))
        self.cb_day.grid(row=0, column=1, sticky="ew", padx=2)
        self.cb_year.grid(row=0, column=2, sticky="ew", padx=(2, 0))

        # Update days when month/year changes
        def _update_days(*_):
            try:
                m = self.month_names.index(self.v_month.get()) + 1
                y = int(self.v_year.get())
                import calendar
                max_day = calendar.monthrange(y, m)[1]
                days = [str(d) for d in range(1, max_day + 1)]
                self.cb_day["values"] = days
                if int(self.v_day.get()) > max_day:
                    self.v_day.set(str(max_day))
            except (ValueError, IndexError):
                pass

        self.v_month.trace_add("write", _update_days)
        self.v_year.trace_add("write", _update_days)
        _update_days()  # Initialize

        # Style comboboxes with proper width
        self.cb_dr = ttk.Combobox(form_panel, textvariable=self.v_dr, width=28, state="disabled")
        self.cb_cr = ttk.Combobox(form_panel, textvariable=self.v_cr, width=28, state="disabled")
        amount_frame = ttk.Frame(form_panel, style="Panel.TFrame")
        amount_frame.grid(row=1, column=3, sticky="ew", padx=(0, SP3), pady=(SP2, SP4))
        amount_frame.columnconfigure(1, weight=1)
        ttk.Label(amount_frame, text="₱", style="FieldLabel.TLabel", background=BG_PANEL).grid(
            row=0, column=0, sticky="w", padx=(0, SP1)
        )
        self.e_amt = ttk.Entry(amount_frame, textvariable=self.v_amt, width=14, font=F_MONO,
                               justify="right", state="readonly")
        self.e_amt.grid(row=0, column=1, sticky="ew")
        self.e_desc = ttk.Entry(form_panel, textvariable=self.v_desc, width=42, state="readonly")

        self.cb_dr.grid(row=1, column=1, sticky="ew", padx=(0, SP3), pady=(SP2, SP4))
        self.cb_cr.grid(row=1, column=2, sticky="ew", padx=(0, SP3), pady=(SP2, SP4))
        self.e_desc.grid(row=1, column=4, sticky="ew", padx=(0, 0), pady=(SP2, SP4))

        # Lock/unlock on click: click to edit, click outside to lock
        def _unlock_entry(widget):
            widget.configure(state="normal")
            if isinstance(widget, ttk.Entry):
                widget.icursor("end")
            elif isinstance(widget, ttk.Combobox):
                widget.after(10, lambda: widget.event_generate("<Down>"))
            widget.focus_set()

        def _lock_all_entries(event=None):
            for w in (self.cb_month, self.cb_day, self.cb_year, self.cb_dr, self.cb_cr, self.e_amt, self.e_desc):
                if str(w.cget("state")) == "normal":
                    if isinstance(w, ttk.Combobox):
                        w.configure(state="disabled")
                    else:
                        w.configure(state="readonly")

        # Click to unlock - use ButtonRelease to allow combobox dropdown to open
        for w in (self.cb_month, self.cb_day, self.cb_year, self.e_amt, self.e_desc):
            w.bind("<Button-1>", lambda e, w=w: (_lock_all_entries(), _unlock_entry(w))[1])
        for cb in (self.cb_dr, self.cb_cr):
            cb.bind("<Button-1>", lambda e, w=cb: (_lock_all_entries(), _unlock_entry(w))[1])

        # Click outside (on form) locks all
        form_panel.bind("<Button-1>", _lock_all_entries)
        for w in (self.cb_month, self.cb_day, self.cb_year, self.cb_dr, self.cb_cr, self.e_amt, self.e_desc):
            w.bind("<FocusOut>", lambda e: _lock_all_entries())

        # Bind Enter to submit from any field (only works when unlocked)
        for w in (self.cb_month, self.cb_day, self.cb_year, self.cb_dr, self.cb_cr, self.e_amt, self.e_desc):
            w.bind("<Return>", lambda _e: self.add_entry())

        # Autocomplete on comboboxes (only when unlocked)
        for cb in (self.cb_dr, self.cb_cr):
            cb.bind("<KeyRelease>", self.filter_accounts)
            cb.bind("<FocusIn>", lambda _e: self.refresh_account_combos())

        # Row 2: Checkbox + Add/Update button + Cancel button + Delete button + status
        bottom = ttk.Frame(form_panel, style="Panel.TFrame")
        bottom.grid(row=2, column=0, columnspan=5, sticky="ew", pady=(SP2, 0))

        # Adjusting entry checkbox (custom canvas-drawn from team version)
        adj_control = tk.Canvas(
            bottom, width=1, height=38, background=BG_PANEL,
            highlightthickness=0, bd=0, cursor="hand2",
        )
        adj_control.pack(side="left", anchor="center", padx=(0, SP4))
        adj_box = tk.Canvas(
            adj_control, width=18, height=18, background=BG_ALT,
            highlightthickness=0, bd=0, cursor="hand2", takefocus=True,
        )
        adj_label = ttk.Label(
            adj_control, text="Adjusting Entry", font=("Segoe UI", 11),
            foreground=TEXT, background=BG_ALT,
        )
        label_width = adj_label.winfo_reqwidth()
        control_width = max(240, 50 + label_width)
        control_height = 38
        adj_control.configure(width=control_width)
        checkbox_left = 11
        center_y = control_height / 2
        adj_control.create_window(checkbox_left + 9, center_y, window=adj_box,
                                  width=18, height=18, anchor="center")
        adj_control.create_window(checkbox_left + 18 + 8, center_y,
                                  window=adj_label, anchor="w")
        radius = 5
        outline_points = []
        corners = (
            (control_width - radius - 1, radius + 1, -90, 0),
            (control_width - radius - 1, control_height - radius - 1, 0, 90),
            (radius + 1, control_height - radius - 1, 90, 180),
            (radius + 1, radius + 1, 180, 270),
        )
        for cx, cy, start, end in corners:
            for angle in range(start, end + 1, 15):
                radians = math.radians(angle)
                outline_points.extend((cx + radius * math.cos(radians),
                                       cy + radius * math.sin(radians)))
        border = adj_control.create_polygon(
            *outline_points, fill=BG_ALT, outline=BORDER_STRONG, width=1,
        )
        adj_control.tag_lower(border)

        def _draw_adjusting_checkbox(*_):
            adj_box.delete("all")
            checked = self.v_adj.get()
            adj_box.create_rectangle(
                1, 1, 17, 17, fill=PRIMARY if checked else BG_ALT,
                outline=PRIMARY, width=1,
            )
            if checked:
                adj_box.create_line(4, 9, 7, 12, 14, 5, fill=TEXT_INVERTED, width=2,
                                    capstyle="round", joinstyle="round")

        def _toggle_adjusting_checkbox(_event=None):
            self.v_adj.set(not self.v_adj.get())

        adj_box.bind("<Button-1>", _toggle_adjusting_checkbox)
        adj_box.bind("<space>", _toggle_adjusting_checkbox)
        adj_box.bind("<Return>", _toggle_adjusting_checkbox)
        adj_label.bind("<Button-1>", _toggle_adjusting_checkbox)
        adj_control.bind("<Button-1>", _toggle_adjusting_checkbox)
        self.v_adj.trace_add("write", _draw_adjusting_checkbox)
        _draw_adjusting_checkbox()

        # Add/Update button (text changes when editing)
        self.add_btn = ttk.Button(
            bottom,
            text="＋  Add Entry",
            style="Primary.TButton",
            command=self.add_entry
        )
        self.add_btn.pack(side="right", padx=(SP3, 0))
        # Hover effect for Primary.TButton
        self.add_btn.bind("<Enter>", lambda e: e.widget.state(["active"]))
        self.add_btn.bind("<Leave>", lambda e: e.widget.state(["!active"]))

        # Delete button (hidden initially, shown when editing)
        self.delete_btn = ttk.Button(
            bottom,
            text="Delete Entry",
            style="Danger.TButton",
            command=self.delete_entry
        )
        # Don't pack initially

        # Cancel button (hidden initially, shown when editing)
        self.cancel_btn = ttk.Button(
            bottom,
            text="Cancel",
            style="Ghost.TButton",
            command=self.cancel_edit
        )
        # Don't pack initially

        # Status / validation message (canvas-rendered rounded badge from team version)
        self.status_var = tk.StringVar(value="")
        self._status_kind = "error"
        self.status_lbl = tk.Canvas(bottom, width=1, height=1, background=BG_PANEL,
                                    highlightthickness=0, bd=0)
        self.status_lbl.pack(side="left", padx=(SP4, 0), anchor="center")
        self.status_var.trace_add("write", self._render_status)

        # Thin separator between form and search bar (team version pattern)
        tk.Frame(tab, height=1, background=BORDER_STRONG, bd=0, highlightthickness=0).pack(fill="x", padx=SP6)

        # ─── Search & Filter Bar ─────────────────────────────────────────────
        search_bar = ttk.Frame(tab, style="Panel.TFrame", padding=(SP4, SP3))
        search_bar.pack(fill="x", padx=SP6, pady=(SP3, SP4))

        ttk.Label(search_bar, text="⌕  Search", style="Muted.TLabel", background=COLOR_BG_PANEL).pack(side="left", padx=(0, SP3))
        self._search_placeholder = "Search journal entries..."
        self.v_search = tk.StringVar(value=self._search_placeholder)
        self.v_search.trace_add("write", lambda *_: self.apply_search_filter())
        self.search_entry = ttk.Entry(search_bar, textvariable=self.v_search, width=45)
        self.search_entry.pack(side="left", padx=(0, SP2))
        self.search_entry.bind("<FocusIn>", self._search_focus_in)
        self.search_entry.bind("<FocusOut>", self._search_focus_out)

        # Custom Clear button (canvas-rendered from team version)
        clear_text = "⌫  Clear"
        clear_font = tkfont.Font(root=self.root, font=("Segoe UI", 12))
        clear_width = max(96, clear_font.measure(clear_text) + 24)
        clear_height = 40
        self.clear_btn = tk.Canvas(
            search_bar, width=clear_width, height=clear_height, background=BG_PANEL,
            highlightthickness=0, bd=0, cursor="hand2", takefocus=True,
        )
        self.clear_btn.pack(side="left")
        clear_state = {"pressed": False}

        def _draw_clear_button(_event=None):
            canvas = self.clear_btn
            canvas.delete("all")
            if clear_state["pressed"]:
                fill, foreground, outline = PRIMARY, TEXT_INVERTED, PRIMARY
            elif canvas.winfo_containing(canvas.winfo_pointerx(), canvas.winfo_pointery()) is canvas:
                # Hover checked before focus - mouse interaction takes priority over keyboard focus
                fill, foreground, outline = PRIMARY_HOVER, TEXT_INVERTED, PRIMARY_HOVER
            elif canvas.focus_get() is canvas:
                fill, foreground, outline = BG_ALT, TEXT, PRIMARY_FOCUS
            else:
                fill, foreground, outline = BG_PANEL, TEXT, BORDER_STRONG

            radius = 6
            points = []
            corners = (
                (clear_width - radius - 1, radius + 1, -90, 0),
                (clear_width - radius - 1, clear_height - radius - 1, 0, 90),
                (radius + 1, clear_height - radius - 1, 90, 180),
                (radius + 1, radius + 1, 180, 270),
            )
            for cx, cy, start, end in corners:
                for angle in range(start, end + 1, 15):
                    radians = math.radians(angle)
                    points.extend((cx + radius * math.cos(radians),
                                   cy + radius * math.sin(radians)))
            canvas.create_polygon(*points, fill=fill, outline=outline, width=1)
            canvas.create_text(clear_width / 2, clear_height / 2, text=clear_text, font=clear_font,
                               fill=foreground, anchor="center")

        def _clear_press(_event=None):
            clear_state["pressed"] = True
            self.clear_btn.focus_set()
            _draw_clear_button()

        def _clear_release(event=None):
            was_pressed = clear_state["pressed"]
            clear_state["pressed"] = False
            _draw_clear_button()
            if was_pressed and (event is None or 0 <= event.x <= clear_width and 0 <= event.y <= clear_height):
                self.clear_search()

        self.clear_btn.bind("<Enter>", _draw_clear_button)
        self.clear_btn.bind("<Leave>", _draw_clear_button)
        self.clear_btn.bind("<FocusIn>", _draw_clear_button)
        self.clear_btn.bind("<FocusOut>", _draw_clear_button)
        self.clear_btn.bind("<ButtonPress-1>", _clear_press)
        self.clear_btn.bind("<ButtonRelease-1>", _clear_release)
        self.clear_btn.bind("<KeyPress-space>", _clear_press)
        self.clear_btn.bind("<KeyRelease-space>", lambda _e: _clear_release())
        self.clear_btn.bind("<KeyPress-Return>", _clear_press)
        self.clear_btn.bind("<KeyRelease-Return>", lambda _e: _clear_release())
        _draw_clear_button()

        ttk.Separator(search_bar, orient="vertical").pack(side="left", fill="y", padx=SP4)

        self.search_info = tk.StringVar(value="")
        ttk.Label(search_bar, textvariable=self.search_info, style="Counter.TLabel").pack(side="left")

        # ─── Selection Toolbar (shows when entries are selected) ───────────────
        self.selection_toolbar = ttk.Frame(tab, style="Panel.TFrame")
        # Initially hidden - will show when selections exist
        self.selection_count_var = tk.StringVar(value="")
        ttk.Label(self.selection_toolbar, textvariable=self.selection_count_var, style="Muted.TLabel").pack(side="left", padx=(SP6, SP3))
        ttk.Button(self.selection_toolbar, text="Delete Selected", style="Danger.TButton",
                   command=self._delete_selected_from_toolbar).pack(side="left", padx=(0, SP3))
        ttk.Button(self.selection_toolbar, text="Clear Selection", style="Ghost.TButton",
                   command=self._clear_selection_from_toolbar).pack(side="left")

        # Thin separator between search bar and table (team version pattern)
        tk.Frame(tab, height=1, background=BORDER_STRONG, bd=0, highlightthickness=0).pack(fill="x", padx=SP6)

        # ─── Journal Table ───────────────────────────────────────────────────
        # Traditional format: Date | Particulars | Dr | Cr
        # 3 lines per entry:
        #   1. Date | Debit Account | Dr Amount |
        #   2.      |   Credit Account | | Cr Amount
        #   3.      |   Description | |
        self.jt = JournalTable(tab)
        self.jt.pack(fill="both", expand=True, padx=SP6, pady=(SP3, SP6))

        # Bind callbacks
        self.jt.bind_select(self._on_selection_changed)
        self.jt.bind_edit(lambda eidx: self.edit_entry(eidx))
        self.jt.bind_context(self._show_context_menu)
        self.jt.bind_delete(self.delete_multiple_entries)

        # Keyboard shortcuts
        self.root.bind("<Control-f>", lambda _e: self.search_entry.focus_set())
        self.root.bind("<Control-n>", lambda _e: self.focus_new_entry())

        # Note: refresh() is called by main.py after all tabs are built

    def _create_context_menu(self):
        """Right-click context menu for journal table."""
        self.ctx_menu = tk.Menu(self.root, tearoff=0)
        self.ctx_menu.add_command(label="Edit", command=lambda: self.edit_entry(None))
        self.ctx_menu.add_command(label="Delete", command=self.delete_entry)
        # Context menu handled by JournalTable.bind_context

    def _show_context_menu(self, event, entry_idx=None):
        """Show context menu on right-click."""
        if entry_idx is not None:
            self.ctx_menu.tk_popup(event.x_root, event.y_root)

    def filter_accounts(self, ev):
        if ev.keysym in ("Up", "Down", "Left", "Right", "Return", "Tab", "Escape", "Shift_L", "Shift_R"):
            return
        t = ev.widget.get().strip().lower()
        names = self.all_account_names()
        ev.widget["values"] = [n for n in names if t in n.lower()] or names

    def refresh_account_combos(self):
        """Refresh combobox values with current account list."""
        names = self.all_account_names()
        self.cb_dr["values"] = names
        self.cb_cr["values"] = names

    def ask_type(self, name):
        dlg = tk.Toplevel(self.root)
        dlg.title("New Account")
        dlg.transient(self.root)
        dlg.resizable(False, False)
        dlg.geometry(f"+{self.root.winfo_rootx() + 420}+{self.root.winfo_rooty() + 260}")
        dlg.configure(background=BG_PANEL)
        ttk.Label(dlg, text=f'"{name}" is not in the list.\nWhat type of account is it?',
                  padding=SP4, justify="center", background=BG_PANEL,
                  foreground=TEXT).pack()
        var = tk.StringVar(value=ASSET)
        cb = ttk.Combobox(dlg, textvariable=var, values=TYPES, state="readonly", width=24)
        cb.pack(padx=SP4, pady=(0, SP4))
        res = {"v": None}

        def ok(_=None):
            res["v"] = var.get()
            dlg.destroy()

        ttk.Button(dlg, text="OK", style="Primary.TButton", command=ok).pack(pady=(0, SP4))
        dlg.bind("<Return>", lambda _e: ok())
        dlg.bind("<Escape>", lambda _e: dlg.destroy())
        cb.focus_set()
        dlg.wait_visibility()
        dlg.grab_set()
        dlg.wait_window()
        return res["v"]

    def resolve(self, raw):
        """Match typed text to a known account (any case) or ask for the type of a new one.
        Returns (account_name, is_new, account_type) or (None, False, None) if cancelled.
        Does NOT add to self.custom — caller must do that after both accounts resolve.
        """
        for n in self.all_account_names():
            if n.lower() == raw.lower():
                return n, False, None
        t = self.ask_type(raw)
        if t is None:
            return None, False, None
        return raw, True, t

    def _validate_form(self):
        """Validate all form fields. Returns (is_valid, error_message, widget)."""
        # Get date from comboboxes
        try:
            m = self.month_names.index(self.v_month.get()) + 1
            d = int(self.v_day.get())
            y = int(self.v_year.get())
            # Validate date
            import datetime
            datetime.date(y, m, d)
            iso_date = f"{y:04d}-{m:02d}-{d:02d}"
        except (ValueError, IndexError):
            return False, "Invalid date", self.cb_day

        dr_raw = " ".join(self.v_dr.get().split())
        cr_raw = " ".join(self.v_cr.get().split())

        # Debit account
        if not dr_raw:
            return False, "Debit account is required", self.cb_dr

        # Credit account
        if not cr_raw:
            return False, "Credit account is required", self.cb_cr

        # Different accounts
        if dr_raw.lower() == cr_raw.lower():
            return False, "Debit and credit accounts must be different", self.cb_cr

        # Amount
        try:
            txt = self.v_amt.get().replace(",", "").replace("₱", "").replace("$", "").strip()
            if not txt:
                return False, "Amount is required", self.e_amt
            amt = Decimal(txt)
            if not amt.is_finite() or amt <= 0:
                raise InvalidOperation
            amt = amt.quantize(Decimal("0.01"))
        except InvalidOperation:
            return False, "Enter a valid positive amount (e.g., 1000.00)", self.e_amt

        return True, iso_date, None

    def _show_error(self, widget, message):
        """Show validation error on a widget."""
        if isinstance(widget, ttk.Combobox):
            widget.configure(style="Error.TCombobox")
        else:
            widget.configure(style="Error.TEntry")
        self._status_kind = "error"
        self.status_var.set(message)
        self.root.after(3000, lambda: self._clear_error(widget))

    def _clear_error(self, widget):
        """Clear validation error styling."""
        if widget in (self.e_amt,):
            widget.configure(style="TEntry")
        else:
            widget.configure(style="TCombobox")
        if self.status_var.get():
            self.status_var.set("")

    def _show_success(self, message):
        """Show brief success message that fades."""
        self._status_kind = "success"
        self.status_var.set(message)
        self.root.after(2500, lambda: self.status_var.set(""))

    def _render_status(self, *_):
        """Draw the inline status as a compact, rounded theme-colored badge."""
        canvas = self.status_lbl
        canvas.delete("all")
        message = self.status_var.get()
        if not message:
            canvas.configure(width=1, height=1)
            return

        font = tkfont.Font(root=self.root, font=("Segoe UI", 12))
        width = font.measure(message) + 20
        height = 28
        canvas.configure(width=width, height=height)
        if self._status_kind == "error":
            fill, outline, foreground = COLOR_DANGER_LIGHT, BORDER_STRONG, COLOR_DANGER
        elif self._status_kind == "success":
            fill, outline, foreground = COLOR_SUCCESS_LIGHT, BORDER_STRONG, COLOR_SUCCESS
        else:
            fill, outline, foreground = BG_PANEL, BG_PANEL, TEXT_MUTED

        radius = 4
        points = []
        corners = (
            (width - radius - 1, radius + 1, -90, 0),
            (width - radius - 1, height - radius - 1, 0, 90),
            (radius + 1, height - radius - 1, 90, 180),
            (radius + 1, radius + 1, 180, 270),
        )
        for cx, cy, start, end in corners:
            for angle in range(start, end + 1, 15):
                radians = math.radians(angle)
                points.extend((cx + radius * math.cos(radians),
                               cy + radius * math.sin(radians)))
        canvas.create_polygon(*points, fill=fill, outline=outline, width=1)
        canvas.create_text(width / 2, height / 2, text=message, font=font,
                           fill=foreground, anchor="center")

    def _journal_dialog(self, title, message, kind="info", confirm=False):
        """Show a small modal Journal dialog using the application's palette."""
        dlg = tk.Toplevel(self.root)
        dlg.title(title)
        dlg.transient(self.root)
        dlg.resizable(False, False)
        dlg.configure(background=BG_PANEL)
        ttk.Style().configure("JournalDialog.TFrame", background=BG_PANEL,
                              borderwidth=1, bordercolor=BORDER_STRONG, relief="solid")
        body = ttk.Frame(dlg, style="JournalDialog.TFrame", padding=SP4)
        body.pack(fill="both", expand=True)
        foreground = COLOR_DANGER if kind == "warning" else TEXT
        ttk.Label(body, text=title, font=("Segoe UI", 12, "bold"),
                  background=BG_PANEL, foreground=TEXT).pack(anchor="w", pady=(0, SP2))
        ttk.Label(body, text=message, justify="left", wraplength=440,
                  background=BG_PANEL, foreground=foreground).pack(fill="x")

        result = {"confirmed": False}
        actions = ttk.Frame(body, style="Panel.TFrame")
        actions.pack(fill="x", pady=(SP4, 0))

        def close(confirmed=False):
            result["confirmed"] = confirmed
            dlg.destroy()

        if confirm:
            ttk.Button(actions, text="No", style="Ghost.TButton",
                       command=lambda: close()).pack(side="right", padx=(SP2, 0))
            ttk.Button(actions, text="Yes", style="Primary.TButton",
                       command=lambda: close(True)).pack(side="right")
        else:
            ttk.Button(actions, text="OK", style="Primary.TButton",
                       command=lambda: close(True)).pack(side="right")

        dlg.bind("<Escape>", lambda _e: close())
        dlg.bind("<Return>", lambda _e: close(confirm))
        dlg.protocol("WM_DELETE_WINDOW", lambda: close())
        dlg.update_idletasks()
        x = self.root.winfo_rootx() + (self.root.winfo_width() - dlg.winfo_width()) // 2
        y = self.root.winfo_rooty() + (self.root.winfo_height() - dlg.winfo_height()) // 2
        dlg.geometry(f"+{max(0, x)}+{max(0, y)}")
        dlg.grab_set()
        dlg.wait_window()
        return result["confirmed"]

    def add_entry(self):
        valid, msg, widget = self._validate_form()
        if not valid:
            self._show_error(widget, msg)
            return

        # msg now contains the ISO date from validation
        iso_date = msg
        dr_raw = " ".join(self.v_dr.get().split())
        cr_raw = " ".join(self.v_cr.get().split())
        txt = self.v_amt.get().replace(",", "").replace("₱", "").replace("$", "").strip()
        amt = Decimal(txt).quantize(Decimal("0.01"))

        dr, dr_new, dr_type = self.resolve(dr_raw)
        if not dr:
            return
        cr, cr_new, cr_type = self.resolve(cr_raw)
        if not cr:
            return

        # Take snapshot BEFORE any changes to entries or custom
        entries_snapshot = copy.deepcopy(self.entries)
        custom_snapshot = copy.deepcopy(self.custom)

        # Only add custom accounts after BOTH resolve successfully
        if dr_new:
            self.custom[dr] = dr_type
        if cr_new:
            self.custom[cr] = cr_type

        # Store description as-is; empty string stays empty
        desc = self.v_desc.get().strip()

        new_entry = {"date": iso_date, "debit": dr, "credit": cr, "amount": str(amt),
                     "desc": desc, "adj": self.v_adj.get()}

        # Check if editing
        is_edit = hasattr(self, '_editing_index') and self._editing_index is not None
        if is_edit:
            self.entries[self._editing_index] = new_entry
        else:
            self.entries.append(new_entry)

        self.sync_custom_accounts()  # Clean up orphaned custom accounts
        if not self.save():
            # Save failed: restore snapshot, refresh, keep form as-is, don't show success
            self.entries = entries_snapshot
            self.custom = custom_snapshot
            self.refresh()
            return

        # Save succeeded
        if is_edit:
            self._show_success("Entry updated")
        else:
            self._show_success("Entry added")
        self._editing_index = None
        self.refresh()

        # Clear form and focus debit account
        for v in (self.v_dr, self.v_cr, self.v_amt, self.v_desc):
            v.set("")
        self.v_adj.set(False)
        self._reset_form_for_new_entry()

    def _reset_form_for_new_entry(self):
        """Reset form to 'add new entry' state."""
        self.add_btn.configure(text="＋  Add Entry")
        self.cancel_btn.pack_forget()
        self.delete_btn.pack_forget()
        # Reset date to today
        today = date.today()
        self.v_month.set(today.strftime("%b"))
        self.v_day.set(str(today.day))
        self.v_year.set(str(today.year))
        self.cb_dr.focus_set()

    def cancel_edit(self):
        """Cancel editing and reset form to new entry state."""
        self._editing_index = None
        for v in (self.v_dr, self.v_cr, self.v_amt, self.v_desc):
            v.set("")
        today = date.today()
        self.v_month.set(today.strftime("%b"))
        self.v_day.set(str(today.day))
        self.v_year.set(str(today.year))
        self.v_adj.set(False)
        self._reset_form_for_new_entry()
        self.status_var.set("")

    def edit_entry(self, entry_idx=None):
        """Edit an entry. If entry_idx is None, use current selection."""
        if entry_idx is None:
            sel = self.jt.get_selection()
            if not sel:
                return self._journal_dialog("Edit", "Click an entry in the journal first.")
            # Parse entry_idx from selection
            entry_idx = int(sel.split("_")[0])

        entry = self.entries[entry_idx]

        # Parse ISO date (YYYY-MM-DD) to month/day/year
        iso_date = entry["date"]
        try:
            y, m, d = map(int, iso_date.split("-"))
            self.v_month.set(self.month_names[m - 1])
            self.v_day.set(str(d))
            self.v_year.set(str(y))
        except (ValueError, IndexError):
            today = date.today()
            self.v_month.set(today.strftime("%b"))
            self.v_day.set(str(today.day))
            self.v_year.set(str(today.year))

        self.v_dr.set(entry["debit"])
        self.v_cr.set(entry["credit"])
        self.v_amt.set(entry["amount"])
        self.v_desc.set(entry.get("desc", ""))
        self.v_adj.set(entry.get("adj", False))

        self._editing_index = entry_idx
        self.cb_month.focus_set()
        self._status_kind = "muted"
        self.status_var.set(f"Editing entry {entry_idx + 1}. Modify values and click 'Update Entry' to save, or 'Cancel' to discard.")
        # Show cancel button, delete button, change add button text
        self.add_btn.configure(text="Update Entry")
        self.cancel_btn.pack(side="right", padx=(0, SP3))
        self.delete_btn.pack(side="right", padx=(0, SP3))

    def delete_entry(self):
        """Delete single entry (backward compatible - uses current selection)."""
        sel = self.jt.get_selection()
        if not sel:
            return self._journal_dialog("Delete", "Select an entry first.")
        entry_idx = int(sel.split("_")[0])
        self.delete_multiple_entries([entry_idx])

    def delete_multiple_entries(self, entry_indices):
        """Delete multiple entries by index."""
        if not entry_indices:
            return self._journal_dialog("Delete", "Select entries first.")

        count = len(entry_indices)
        if count == 1:
            entry = self.entries[entry_indices[0]]
            amount = fmt_amt(Decimal(entry["amount"]))
            detail = f"Debit: {entry['debit']}\nCredit: {entry['credit']}\nAmount: {amount}\nDate: {date_to_display(entry['date'])}"
            msg = f"Delete this entry?\n\n{detail}\n\nThis cannot be undone."
        else:
            msg = f"Delete {count} selected entries?\n\nThis cannot be undone."

        if self._journal_dialog("Delete Entries", msg, kind="warning", confirm=True):
            # Take snapshot BEFORE deleting
            entries_snapshot = copy.deepcopy(self.entries)
            custom_snapshot = copy.deepcopy(self.custom)

            # Delete in reverse order to maintain correct indices
            for idx in sorted(entry_indices, reverse=True):
                del self.entries[idx]
            self.sync_custom_accounts()  # Clean up orphaned custom accounts
            if not self.save():
                # Save failed: restore snapshot, refresh, keep selection
                self.entries = entries_snapshot
                self.custom = custom_snapshot
                self.refresh()
                return

            # Save succeeded
            self.refresh()
            # Clear selection in journal table
            self.jt.clear_selection()
            self._on_selection_changed(0, "")
            self.jt.body.focus_set()
            self._show_success(f"{count} entry{'s' if count > 1 else ''} deleted")

    def _on_selection_changed(self, _entry_idx, _line_type):
        """Called when selection changes in the journal table."""
        selections = self.jt.get_selections()
        if selections:
            self.selection_count_var.set(f"{len(selections)} entr{'y' if len(selections) == 1 else 'ies'} selected")
            self.selection_toolbar.pack(fill="x", padx=SP6, pady=(SP3, 0), before=self.jt)
        else:
            self.selection_toolbar.pack_forget()

    def _delete_selected_from_toolbar(self):
        """Delete button in selection toolbar."""
        selections = self.jt.get_selections()
        if selections:
            self.delete_multiple_entries(selections)

    def _clear_selection_from_toolbar(self):
        """Clear selection button in selection toolbar."""
        self.jt.clear_selection()
        self._on_selection_changed(0, "")
        self.jt.body.focus_set()

    def clear_search(self):
        self.v_search.set(self._search_placeholder)
        self.refresh()

    def _search_focus_in(self, _event=None):
        if self.v_search.get() == self._search_placeholder:
            self.v_search.set("")

    def _search_focus_out(self, _event=None):
        if not self.v_search.get().strip():
            self.v_search.set(self._search_placeholder)

    def apply_search_filter(self):
        search_text = self.v_search.get().strip().lower()
        if search_text == self._search_placeholder.lower():
            search_text = ""

        if not search_text:
            filtered = list(enumerate(self.entries))
        else:
            filtered = []
            for i, e in enumerate(self.entries):
                searchable = f"{e['debit']} {e['credit']} {e.get('desc', '')} {date_to_display(e['date'])} {e['amount']}".lower()
                if search_text in searchable:
                    filtered.append((i, e))

        # Sort by date (oldest first), then by original index for stability
        filtered.sort(key=lambda x: (x[1]["date"], x[0]))

        total = len(self.entries)
        shown = len(filtered)
        if search_text:
            self.search_info.set(f"{shown} of {total} entries")
        else:
            self.search_info.set(f"{total} {'entry' if total == 1 else 'entries'}")

        self.refresh_journal_with_filter(filtered)

    def refresh_journal(self):
        self.apply_search_filter()

    def refresh_journal_with_filter(self, filtered_entries):
        """Refresh journal table with filtered entries using JournalTable."""
        rows = []
        for idx, (i, e) in enumerate(filtered_entries):
            a = Decimal(e["amount"])
            tag_base = ("adj",) if e["adj"] else ()
            display_date = date_to_display(e["date"])
            amt_fmt = fmt_amt(a)

            # Line 1: Debit line - Date | Debit Account | Dr Amount |
            rows.append((i, "debit", (display_date, e["debit"], amt_fmt, ""), tag_base + ("entry_start",)))

            # Line 2: Credit line - (blank) |   Credit Account | | Cr Amount
            rows.append((i, "credit", ("", f"    {e['credit']}", "", amt_fmt), tag_base + ("credit_line", "entry_mid")))

            # Line 3: Description line - (blank) |   Description | |
            desc = e.get("desc", "")
            if desc:
                rows.append((i, "desc", ("", f"    {desc}", "", ""), tag_base + ("desc_line", "entry_end")))

            # Add separator line after each entry (except the last one)
            if idx < len(filtered_entries) - 1:
                rows.append((i, "separator", ("", "", "", ""), ("separator",)))

        self.jt.set_rows(rows)