"""Journal Table — Canvas-based table with thin separator lines between entries."""
import tkinter as tk
from tkinter import ttk
from decimal import Decimal

from style import (
    BG, BG_ALT, BORDER, BORDER_STRONG, TEXT, TEXT_MUTED, WARNING_LIGHT, PRIMARY, PRIMARY_HOVER, PRIMARY_LIGHT,
    F_XS, F_SM, F_MONO,
    SP2, SP3, SP4,
    ROW_H, HEAD_H,
)


class JournalTable(ttk.Frame):
    """Canvas-based journal table with proper thin separator lines and optional checkbox column."""

    # Normal mode (no checkbox): date=15%, particulars=40%, dr=22.5%, cr=22.5%
    NORMAL_COLUMNS = ("date", "particulars", "dr", "cr")
    NORMAL_HEADERS = ("Date", "Particulars", "Dr", "Cr")
    NORMAL_COL_RATIOS = [0.15, 0.40, 0.225, 0.225]

    # Selection mode (with checkbox): checkbox=5%, date=14%, particulars=38%, dr=21.5%, cr=21.5%
    SELECTION_COLUMNS = ("", "date", "particulars", "dr", "cr")
    SELECTION_HEADERS = ("", "Date", "Particulars", "Dr", "Cr")
    SELECTION_COL_RATIOS = [0.05, 0.14, 0.38, 0.215, 0.215]

    CHECKBOX_SIZE = 16

    def __init__(self, parent):
        super().__init__(parent)
        self._rows = []  # List of (entry_idx, line_type, values, tags)
        self._entry_count = 0
        self._selected_iids = set()  # Multiple selected IIDs for multi-select
        self._select_callback = None
        self._delete_callback = None
        self._edit_callback = None
        self._context_callback = None
        self._anchor_iid = None  # For Shift+click range selection
        self._header_select_all = False  # State of header checkbox
        self._selection_mode = False  # Whether checkbox column is visible

        self.row_h = ROW_H
        self.head_h = HEAD_H
        self.pad = 1

        # Header canvas
        self.head = tk.Canvas(self, height=self.head_h, highlightthickness=0, bg=BG,
                              xscrollincrement=20)
        # Body canvas
        self.body = tk.Canvas(self, highlightthickness=0, bg=BG_ALT, yscrollincrement=self.row_h,
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

        # Click/selection bindings - support Ctrl/Shift multi-select
        self.body.bind("<Button-1>", self._on_click)
        self.body.bind("<Control-Button-1>", self._on_ctrl_click)
        self.body.bind("<Shift-Button-1>", self._on_shift_click)
        self.body.bind("<Double-Button-1>", self._on_double_click)
        self.body.bind("<Button-3>", self._on_right_click)
        self.body.bind("<Button-2>", self._on_right_click)

        # Header checkbox click
        self.head.bind("<Button-1>", self._on_header_click)

        # Keyboard shortcuts
        self.body.bind("<Delete>", self._on_delete_key)
        self.body.bind("<Control-a>", self._on_select_all)
        self.body.bind("<Escape>", self._on_escape)
        self.body.bind("<ButtonPress-1>", lambda e: self.body.focus_set(), add="+")

        self.body.bind("<Configure>", self._on_resize)
        self.body.focus_set()  # Allow keyboard events
        self._layout(1000)  # Initial layout with default width
        self._draw_header()
        self.set_rows([])

    def _get_current_config(self):
        """Get current column config based on selection mode."""
        if self._selection_mode:
            return self.SELECTION_HEADERS, self.SELECTION_COL_RATIOS
        return self.NORMAL_HEADERS, self.NORMAL_COL_RATIOS

    def _layout(self, width):
        """Calculate column x positions based on available width."""
        headers, ratios = self._get_current_config()
        avail = max(400, width - 2 * self.pad)
        self.col_w = []
        self.xs = [self.pad]
        for ratio in ratios:
            w = avail * ratio
            self.col_w.append(w)
            self.xs.append(self.xs[-1] + w)
        self.total_w = self.xs[-1] + self.pad

    def _enter_selection_mode(self):
        """Enter selection mode - show checkbox column."""
        if not self._selection_mode:
            self._selection_mode = True
            self._layout(self.body.winfo_width() or 1000)
            self._draw_header()
            self.set_rows(self._rows, preserve_selection=True)

    def _exit_selection_mode_if_empty(self):
        """Exit selection mode if no selections remain."""
        if self._selection_mode and not self._selected_iids:
            self._selection_mode = False
            self._layout(self.body.winfo_width() or 1000)
            self._draw_header()
            self.set_rows(self._rows, preserve_selection=True)

    def _on_resize(self, event):
        self._layout(event.width)
        self._draw_header()
        self.set_rows(self._rows)

    def _xview(self, *args):
        self.body.xview(*args)
        self.head.xview(*args)

    def _wheel(self, e):
        self.body.yview_scroll(-1 if e.delta > 0 else 1, "units")

    def _hwheel(self, e):
        self._xview("scroll", -3 if e.delta > 0 else 3, "units")

    def _draw_header(self):
        h = self.head
        h.delete("all")
        h.configure(scrollregion=(0, 0, self.total_w, self.head_h))

        headers, _ = self._get_current_config()

        # Header background - use PRIMARY color (from team version)
        h.create_rectangle(0, 0, self.total_w, self.head_h, fill=PRIMARY, outline="")

        # Column headers
        for i, header in enumerate(headers):
            if i == 0 and self._selection_mode:
                # Checkbox column - draw checkbox
                self._draw_checkbox(h, self.xs[0] + (self.col_w[0] - self.CHECKBOX_SIZE) / 2,
                                    self.head_h / 2, self._header_select_all, color="#FFFFFF")
            else:
                x = self.xs[i] + SP3
                anchor = "w" if (i < 2 and not self._selection_mode) or (i < 3 and self._selection_mode) else "e"
                h.create_text(x if anchor == "w" else self.xs[i+1] - SP2,
                              self.head_h / 2, text=header, anchor=anchor,
                              fill="#FFFFFF", font=("Segoe UI", 12, "bold"))

        # Vertical lines in header - use PRIMARY_HOVER for lines (from team version)
        for i, x in enumerate(self.xs):
            width = 2 if i in (0, len(self.xs) - 1) else 1
            h.create_line(x, 0, x, self.head_h, fill=PRIMARY_HOVER, width=width)

        # Bottom border
        h.create_line(self.pad, self.head_h, self.total_w - self.pad, self.head_h,
                      fill=BORDER_STRONG, width=2)

    def _draw_checkbox(self, canvas, x, y, checked, enabled=True, color=None):
        """Draw a checkbox at given position."""
        size = self.CHECKBOX_SIZE
        # Box
        color = color or (PRIMARY if enabled else TEXT_MUTED)
        canvas.create_rectangle(x, y - size/2, x + size, y + size/2,
                                outline=color, width=2, fill="")
        if checked:
            # Check mark
            canvas.create_line(x + 3, y, x + size/2 - 1, y + size/2 - 3,
                               fill=color, width=2)
            canvas.create_line(x + size/2 - 1, y + size/2 - 3, x + size - 3, y - size/2 + 3,
                               fill=color, width=2)

    def _is_debit_line(self, line_type):
        """Check if this is a debit line (the main entry line with checkbox)."""
        return line_type == "debit"

    def _get_col_idx(self, j):
        """Map value index to column index (accounts for checkbox column)."""
        return j + 1 if self._selection_mode else j

    def _get_x_for_col(self, col_idx, anchor_left=True):
        """Get x position for a column index."""
        x = self.xs[col_idx] + SP3
        if not anchor_left:
            x = self.xs[col_idx + 1] - SP2
        return x

    def set_rows(self, rows, preserve_selection=False):
        """rows = list of (entry_idx, line_type, values, tags)
        line_type: 'debit', 'credit', 'desc', 'separator'"""
        self._rows = rows
        b = self.body
        b.delete("all")

        n = len(rows)
        total_h = n * self.row_h
        view_h = max(b.winfo_height(), 1)
        b.configure(scrollregion=(0, 0, self.total_w, max(total_h + 7, view_h)))
        if total_h + 7 <= view_h:
            b.yview_moveto(0)

        # Update header checkbox state
        self._update_header_checkbox_state()

        headers, _ = self._get_current_config()

        for i, (entry_idx, line_type, values, tags) in enumerate(rows):
            y0 = i * self.row_h

            # Determine row style
            is_adj = "adj" in tags
            is_separator = line_type == "separator"
            is_debit = self._is_debit_line(line_type)
            iid = f"{entry_idx}_{line_type}"
            is_selected = (iid in self._selected_iids)

            if is_separator:
                bg = BG
                fg = TEXT
                font = F_XS
            elif is_selected:
                bg = PRIMARY_LIGHT
                fg = PRIMARY
                font = F_SM
            elif is_adj:
                bg = WARNING_LIGHT
                fg = TEXT
                font = F_SM
            elif "odd" in tags or (i // 4) % 2 == 0:
                bg = BG
                fg = TEXT
                font = F_SM
            else:
                bg = BG
                fg = TEXT
                font = F_SM

            # Row background
            if not is_separator:
                b.create_rectangle(self.pad, y0, self.total_w - self.pad, y0 + self.row_h,
                                   fill=bg, outline="")
            else:
                b.create_rectangle(self.pad, y0, self.total_w - self.pad, y0 + self.row_h,
                                   fill=bg, outline="")

            if is_separator:
                # Draw thin black line in the middle of the separator row
                line_y = y0 + self.row_h // 2
                b.create_line(self.pad + 4, line_y, self.total_w - self.pad - 4, line_y,
                              fill=BORDER_STRONG, width=1)
                continue

            # Draw checkbox for debit lines (only in selection mode)
            if self._selection_mode and is_debit:
                cx = self.xs[0] + (self.col_w[0] - self.CHECKBOX_SIZE) / 2
                cy = y0 + self.row_h / 2
                self._draw_checkbox(b, cx, cy, is_selected, enabled=True)

            # Draw cell values
            for j, val in enumerate(values):
                if val:
                    col_idx = self._get_col_idx(j)
                    anchor_left = (col_idx < 2 and not self._selection_mode) or (col_idx < 3 and self._selection_mode)
                    x = self._get_x_for_col(col_idx, anchor_left)

                    cell_font = font
                    cell_fg = fg

                    if "desc_line" in tags:
                        cell_font = ("Segoe UI", 10, "italic")
                        cell_fg = TEXT_MUTED

                    b.create_text(x, y0 + self.row_h / 2, text=val, anchor="w" if anchor_left else "e",
                                  font=cell_font, fill=cell_fg)

            # Vertical grid lines (thin)
            for j, x in enumerate(self.xs):
                if j in (0, len(self.xs) - 1):
                    # Outer borders - thicker
                    b.create_line(x, y0, x, y0 + self.row_h, fill=BORDER, width=2)
                else:
                    b.create_line(x, y0, x, y0 + self.row_h, fill=BORDER, width=1)

            # Horizontal line at bottom of row (thin)
            b.create_line(self.pad, y0 + self.row_h, self.total_w - self.pad, y0 + self.row_h,
                          fill=BORDER, width=1)

        if not rows:
            center_x = self.body.winfo_width() / 2
            center_y = max(84, self.body.winfo_height() / 2)
            b.create_text(center_x, center_y - 24, text="▤", fill=PRIMARY,
                          font=("Segoe UI Symbol", 28), anchor="center")
            b.create_text(center_x, center_y + 8, text="No journal entries yet.", fill=TEXT,
                          font=("Segoe UI", 14, "bold"), anchor="center")
            b.create_text(center_x, center_y + 34,
                          text="Add a transaction using the form above.", fill=TEXT_MUTED,
                          font=("Segoe UI", 11), anchor="center")

        # Bottom border
        b.create_line(self.pad, total_h, self.total_w - self.pad, total_h,
                      fill=BORDER_STRONG, width=2)

    def _update_header_checkbox_state(self):
        """Update header checkbox: checked if all debit lines selected."""
        debit_iids = {f"{e}_{lt}" for e, lt, _, _ in self._rows if self._is_debit_line(lt)}
        if not debit_iids:
            self._header_select_all = False
        elif self._selected_iids >= debit_iids:  # All debit lines selected
            self._header_select_all = True
        else:
            self._header_select_all = False  # Partial or none

        # Redraw header to update checkbox (only in selection mode)
        if self._selection_mode:
            self._draw_header()

    def _get_row_from_y(self, y):
        """Get row index from canvas y coordinate."""
        return int(y // self.row_h)

    def _on_click(self, event):
        """Handle click for single selection (clears other selections)."""
        x = self.body.canvasx(event.x)
        y = self.body.canvasy(event.y)
        row = self._get_row_from_y(y)

        if 0 <= row < len(self._rows):
            entry_idx, line_type, _, _ = self._rows[row]
            iid = f"{entry_idx}_{line_type}"

            # Check if clicked on checkbox column (for debit lines in selection mode)
            if self._selection_mode and self._is_debit_line(line_type) and x < self.xs[1]:
                # Toggle this entry's selection
                if iid in self._selected_iids:
                    self._selected_iids.discard(iid)
                else:
                    self._selected_iids.add(iid)
                self._anchor_iid = iid
                self.set_rows(self._rows, preserve_selection=True)
                self._exit_selection_mode_if_empty()
                if self._select_callback:
                    self._select_callback(entry_idx, line_type)
                return

            # Single selection - clear others
            self._selected_iids = {iid}
            self._anchor_iid = iid
            self.set_rows(self._rows, preserve_selection=True)
            if self._select_callback:
                self._select_callback(entry_idx, line_type)

    def _on_ctrl_click(self, event):
        """Handle Ctrl+click for toggle selection."""
        x = self.body.canvasx(event.x)
        y = self.body.canvasy(event.y)
        row = self._get_row_from_y(y)

        if 0 <= row < len(self._rows):
            entry_idx, line_type, _, _ = self._rows[row]
            iid = f"{entry_idx}_{line_type}"

            # Check if clicked on checkbox column (for debit lines in selection mode)
            if self._selection_mode and self._is_debit_line(line_type) and x < self.xs[1]:
                # Toggle this entry's selection
                if iid in self._selected_iids:
                    self._selected_iids.discard(iid)
                else:
                    self._selected_iids.add(iid)
                self._anchor_iid = iid
                self.set_rows(self._rows, preserve_selection=True)
                self._exit_selection_mode_if_empty()
                if self._select_callback:
                    self._select_callback(entry_idx, line_type)
                return

            # Toggle this item (enters selection mode)
            if iid in self._selected_iids:
                self._selected_iids.discard(iid)
            else:
                self._selected_iids.add(iid)
                self._enter_selection_mode()
            self._anchor_iid = iid
            self.set_rows(self._rows, preserve_selection=True)
            self._exit_selection_mode_if_empty()
            if self._select_callback:
                self._select_callback(entry_idx, line_type)

    def _on_shift_click(self, event):
        """Handle Shift+click for range selection."""
        x = self.body.canvasx(event.x)
        y = self.body.canvasy(event.y)
        row = self._get_row_from_y(y)

        if 0 <= row < len(self._rows):
            entry_idx, line_type, _, _ = self._rows[row]
            iid = f"{entry_idx}_{line_type}"

            if self._anchor_iid and self._anchor_iid in [f"{e}_{lt}" for e, lt, _, _ in self._rows]:
                # Find range between anchor and clicked
                anchor_row = None
                click_row = row
                for idx, (e, lt, _, _) in enumerate(self._rows):
                    if f"{e}_{lt}" == self._anchor_iid:
                        anchor_row = idx
                        break

                if anchor_row is not None:
                    start, end = sorted([anchor_row, click_row])
                    # Clear and select range (only debit lines)
                    self._selected_iids = set()
                    for r in range(start, end + 1):
                        e, lt, _, _ = self._rows[r]
                        if self._is_debit_line(lt):
                            self._selected_iids.add(f"{e}_{lt}")
                    self._enter_selection_mode()
                    self.set_rows(self._rows, preserve_selection=True)
                    if self._select_callback:
                        self._select_callback(entry_idx, line_type)
                else:
                    self._on_click(event)
            else:
                self._on_click(event)

    def _on_header_click(self, event):
        """Handle click on header checkbox (select all / deselect all)."""
        if not self._selection_mode:
            return
        x = self.head.canvasx(event.x)
        # Check if clicked in checkbox column
        if x < self.xs[1]:
            debit_iids = {f"{e}_{lt}" for e, lt, _, _ in self._rows if self._is_debit_line(lt)}
            if self._selected_iids >= debit_iids:
                # All selected - deselect all
                self._selected_iids.clear()
            else:
                # Select all debit lines
                self._selected_iids = debit_iids.copy()
            self._anchor_iid = None
            self.set_rows(self._rows, preserve_selection=True)
            self._exit_selection_mode_if_empty()
            if self._select_callback and self._selected_iids:
                # Notify with first selected
                first_iid = next(iter(self._selected_iids))
                entry_idx = int(first_iid.split("_")[0])
                self._select_callback(entry_idx, "debit")

    def _on_delete_key(self, event):
        """Handle Delete key for bulk delete."""
        if self._selected_iids and self._delete_callback:
            # Get unique entry indices from selected IIDs
            entry_indices = set()
            for iid in self._selected_iids:
                entry_idx = int(iid.split("_")[0])
                entry_indices.add(entry_idx)
            self._delete_callback(sorted(entry_indices))

    def _notify_selection_changed(self):
        """Tell the Journal tab that the selection changed, so its toolbar updates."""
        if self._select_callback:
            self._select_callback(0, "")

    def _on_select_all(self, event):
        """Handle Ctrl+A to select all entries (debit lines only)."""
        self._selected_iids = set()
        for entry_idx, line_type, _, _ in self._rows:
            if self._is_debit_line(line_type):
                self._selected_iids.add(f"{entry_idx}_{line_type}")
        if self._selected_iids:
            self._enter_selection_mode()
        self._anchor_iid = None
        self.set_rows(self._rows, preserve_selection=True)
        self._exit_selection_mode_if_empty()
        self._notify_selection_changed()        

    def _on_escape(self, event):
        """Handle Escape to clear selection."""
        if self._selected_iids:
            self._selected_iids.clear()
            self._anchor_iid = None
            self.set_rows(self._rows, preserve_selection=True)
            self._notify_selection_changed()
            self._exit_selection_mode_if_empty()

    def _on_double_click(self, event):
        """Handle double-click to edit entry."""
        x = self.body.canvasx(event.x)
        y = self.body.canvasy(event.y)
        row = self._get_row_from_y(y)

        if 0 <= row < len(self._rows):
            entry_idx, line_type, _, _ = self._rows[row]
            # Only trigger edit on debit or credit lines (not desc/separator)
            if line_type in ("debit", "credit") and self._edit_callback:
                self._edit_callback(entry_idx)

    def _on_right_click(self, event):
        """Handle right-click for context menu."""
        x = self.body.canvasx(event.x)
        y = self.body.canvasy(event.y)
        row = self._get_row_from_y(y)

        if 0 <= row < len(self._rows):
            entry_idx, line_type, _, _ = self._rows[row]
            # Only trigger context menu on debit or credit lines (not desc/separator)
            if line_type in ("debit", "credit") and self._context_callback:
                self._context_callback(event, entry_idx)

    def bind_select(self, callback):
        self._select_callback = callback

    def bind_delete(self, callback):
        self._delete_callback = callback

    def bind_edit(self, callback):
        self._edit_callback = callback

    def bind_context(self, callback):
        self._context_callback = callback

    def get_selection(self):
        """Return single selection for backward compatibility, or first selected."""
        if self._selected_iids:
            return next(iter(self._selected_iids))
        return None

    def get_selections(self):
        """Return all selected entry indices (unique)."""
        entry_indices = set()
        for iid in self._selected_iids:
            entry_idx = int(iid.split("_")[0])
            entry_indices.add(entry_idx)
        return sorted(entry_indices)

    def selection_set(self, iid):
        """Set single selection (backward compatible)."""
        self._selected_iids = {iid}
        self._anchor_iid = iid
        self.set_rows(self._rows, preserve_selection=True)

    def clear_selection(self):
        """Clear all selections and exit selection mode."""
        self._selected_iids.clear()
        self._anchor_iid = None
        self.set_rows(self._rows, preserve_selection=True)
        self._exit_selection_mode_if_empty()

    def see(self, iid):
        """Scroll to make item visible."""
        for idx, (eid, lt, _, _) in enumerate(self._rows):
            if f"{eid}_{lt}" == iid:
                y0 = idx * self.row_h
                self.body.yview_moveto(max(0, (y0 - self.row_h * 3) / max(1, self.body.cget("scrollregion") and 1 or 1)))
                break