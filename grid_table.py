"""A table with real grid lines, drawn on a tkinter Canvas — Clean Minimalist design.

Used by the Balance Sheet / Worksheet tab. It only DRAWS what it is given:
call set_rows(...) with the text for every cell. It does no accounting math.

Line style:
  * thin light lines between every row and column
  * thick dark lines around the table and between each Dr/Cr pair
  * a dark line above the first TOTAL row
  * a double line under the GRAND TOTAL row
"""
import tkinter as tk
from tkinter import ttk

from style import (
    BG, BG_PANEL, BORDER, BORDER_STRONG, TEXT, PRIMARY, PRIMARY_LIGHT,
    F_XS, F_SM_BOLD,
    SP2, SP3, ROW_H, HEAD_H,
)


class GridTable(ttk.Frame):
    def __init__(self, parent, first_title, group_titles, sub_labels=("Dr", "Cr"),
                 first_w=280, col_w=96, min_col_w=80, row_h=ROW_H, head_h=HEAD_H):
        super().__init__(parent)
        self.first_title, self.groups, self.subs = first_title, list(group_titles), list(sub_labels)
        self.first_w, self.min_col_w, self.row_h, self.head_h = first_w, min_col_w, row_h, head_h
        self._rows = []
        self.per = len(self.subs)                 # columns per group (Dr, Cr -> 2)
        self.ncols = len(self.groups) * self.per  # total number columns (12)
        self.font = F_XS
        self.bold = F_SM_BOLD
        self.small_bold = ("Segoe UI", 9, "bold")
        self.pad = 1

        self._layout(col_w)

        # Header canvas (2 rows: group titles + Dr/Cr labels)
        self.head = tk.Canvas(self, height=2 * head_h, highlightthickness=0, bg=BG,
                              xscrollincrement=20)
        # Body canvas
        self.body = tk.Canvas(self, highlightthickness=0, bg=BG_PANEL, yscrollincrement=row_h,
                              xscrollincrement=20)
        self.vbar = ttk.Scrollbar(self, orient="vertical", command=self.body.yview)
        self.hbar = ttk.Scrollbar(self, orient="horizontal", command=self._xview)
        self.body.configure(yscrollcommand=self.vbar.set, xscrollcommand=self.hbar.set)
        self.head.grid(row=0, column=0, sticky="ew")
        self.body.grid(row=1, column=0, sticky="nsew")
        self.vbar.grid(row=1, column=1, sticky="ns")
        self.hbar.grid(row=2, column=0, sticky="ew")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        for c in (self.head, self.body):
            c.bind("<MouseWheel>", self._wheel)
            c.bind("<Shift-MouseWheel>", self._hwheel)
            c.bind("<Button-4>", lambda e: self.body.yview_scroll(-1, "units"))
            c.bind("<Button-5>", lambda e: self.body.yview_scroll(1, "units"))

        self.body.bind("<Configure>", self._on_resize)
        self._draw_header()
        self.set_rows([])

    # ---------- layout ----------
    def _layout(self, col_w, avail_width=None):
        """x position of every vertical line: [left edge, after name column, after col 1, ...]
        If avail_width given, last column absorbs remainder to eliminate right margin."""
        self.col_w = col_w
        self.xs = [self.pad, self.pad + self.first_w]
        if avail_width is not None and col_w > 0:
            # Distribute: first ncols-1 columns get col_w, last gets remainder
            for j in range(self.ncols - 1):
                self.xs.append(self.xs[1] + (j + 1) * col_w)
            # Last column gets all remaining space
            self.xs.append(self.pad + self.first_w + avail_width)
        else:
            for j in range(self.ncols):
                self.xs.append(self.xs[1] + (j + 1) * col_w)
        self.total_w = self.xs[-1] + self.pad

    def _on_resize(self, event):
        """Stretch the number columns to fill the window (never narrower than min_col_w).
        Last column gets any remainder to eliminate right margin."""
        avail = event.width - 2 * self.pad - self.first_w
        base_w = max(self.min_col_w, avail // self.ncols)
        if base_w != self.col_w:
            self._layout(base_w, avail)
            self._draw_header()
            self.set_rows(self._rows)

    # ---------- scrolling ----------
    def _xview(self, *args):
        """Scroll header and body together, so the titles stay above their columns."""
        self.body.xview(*args)
        self.head.xview(*args)

    def _wheel(self, e):
        self.body.yview_scroll(-1 if e.delta > 0 else 1, "units")

    def _hwheel(self, e):
        self._xview("scroll", -3 if e.delta > 0 else 3, "units")

    # ---------- line helpers ----------
    def _is_thick(self, k):
        """Vertical line k is thick at the outer edges and after each Dr/Cr pair."""
        return k in (0, 1) or k == len(self.xs) - 1 or (k - 1) % self.per == 0

    # ---------- drawing ----------
    def _draw_header(self):
        h, hh = self.head, self.head_h
        h.delete("all")
        h.configure(scrollregion=(0, 0, self.total_w, 2 * hh))

        # 1. Top header row background (full width) — BG (white)
        h.create_rectangle(0, 0, self.total_w, hh, fill=BG, outline="")

        # 2. "Account Name" cell spans both header rows (first column) — BG (white)
        h.create_rectangle(self.xs[0], 0, self.xs[1], 2 * hh, fill=BG, outline="")
        h.create_text(self.xs[0] + SP3, hh, text=self.first_title, anchor="w",
                      fill=TEXT, font=self.bold)

        # 3. Section titles on top row — TEXT (dark) text
        for g, title in enumerate(self.groups):
            left, right = self.xs[1 + g * self.per], self.xs[1 + (g + 1) * self.per]
            h.create_text((left + right) / 2, hh / 2, text=title, fill=TEXT, font=self.small_bold)

        # 4. Bottom header row background (number columns only) — BG (white)
        h.create_rectangle(self.xs[1], hh, self.total_w, 2 * hh, fill=BG, outline="")

        # 5. Dr / Cr labels on bottom row — TEXT (dark) text
        for j in range(self.ncols):
            h.create_text(self.xs[j + 2] - SP2, hh + hh / 2, text=self.subs[j % self.per],
                          anchor="e", fill=TEXT, font=self.font)

        # 6. Divider between two header rows — BORDER_STRONG
        h.create_line(self.xs[1], hh, self.xs[-1], hh, fill=BORDER_STRONG)

        # 7. Vertical lines in header
        for k, x in enumerate(self.xs):
            if self._is_thick(k):
                # Thick lines (section separators): full height, BORDER_STRONG
                h.create_line(x, 0, x, 2 * hh, fill=BORDER_STRONG, width=2)
            else:
                # Thin lines (Dr/Cr dividers): only in bottom row, BORDER
                h.create_line(x, hh, x, 2 * hh, fill=BORDER)

        # 8. Solid 2 px PRIMARY line along bottom edge of whole header
        h.create_line(0, 2 * hh - 1, self.total_w, 2 * hh - 1, fill=PRIMARY, width=2)

    def set_rows(self, rows):
        """rows = [(label, [text for each of the number columns], tag), ...]
        tag is one of: "" (plain), "odd" (striped), "total", "grand"."""
        self._rows = rows
        b, rh = self.body, self.row_h
        b.delete("all")
        n = len(rows)
        end = n * rh
        b.configure(scrollregion=(0, 0, self.total_w, end + 7))

        for i, (label, cells, tag) in enumerate(rows):
            y0 = i * rh
            font = self.bold if tag in ("total", "grand") else self.font

            # Row background
            if tag == "grand":
                bg = PRIMARY_LIGHT
                fg = PRIMARY
            elif tag == "total":
                bg = BG
                fg = TEXT
            elif tag == "odd":
                bg = BG_PANEL
                fg = TEXT
            else:
                bg = BG_PANEL
                fg = TEXT

            b.create_rectangle(self.xs[0], y0, self.xs[-1], y0 + rh, fill=bg, outline="")
            b.create_text(self.xs[0] + SP3, y0 + rh / 2, text=label, anchor="w", font=font, fill=fg)

            for j, text in enumerate(cells):
                if text:
                    b.create_text(self.xs[j + 2] - SP2, y0 + rh / 2, text=text, anchor="e", font=font, fill=fg)

        # Thin horizontal lines between rows
        for i in range(n + 1):
            b.create_line(self.xs[0], i * rh, self.xs[-1], i * rh, fill=BORDER)

        # Vertical lines
        for k, x in enumerate(self.xs):
            if self._is_thick(k):
                b.create_line(x, 0, x, end, fill=BORDER, width=2)
            else:
                b.create_line(x, 0, x, end, fill=BORDER)

        # Thick line above first TOTAL row
        first_total = next((i for i, r in enumerate(rows) if r[2] == "total"), None)
        if first_total is not None:
            y = first_total * rh
            b.create_line(self.xs[0], y, self.xs[-1], y, fill=BORDER, width=2)

        # Double line under GRAND TOTAL
        if n and rows[-1][2] == "grand":
            for y in (end + 1, end + 4):
                b.create_line(self.xs[0], y, self.xs[-1], y, fill=BORDER, width=2)
        else:
            b.create_line(self.xs[0], end, self.xs[-1], end, fill=BORDER, width=2)