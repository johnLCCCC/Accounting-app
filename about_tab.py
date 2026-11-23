"""About dialog — shown from Help menu."""
import math
import tkinter as tk
from tkinter import ttk

from style import (
    BG, BG_PANEL, BORDER, BORDER_STRONG, PRIMARY, PRIMARY_HOVER,
    TEXT, TEXT_INVERTED, TEXT_MUTED,
    SP2, SP3, SP4, SP6,
)


def show_about(root):
    """Show the centered, two-column About dialog."""
    dlg = tk.Toplevel(root)
    dlg.title("About Accounting App")
    dlg.transient(root)
    dlg.configure(background=BG)
    dlg.resizable(True, True)
    screen_w, screen_h = dlg.winfo_screenwidth(), dlg.winfo_screenheight()
    width = max(440, min(820, screen_w - 48))
    height = max(400, min(700, screen_h - 80))
    dlg.minsize(min(600, width), min(500, height))
    dlg.geometry(f"{width}x{height}")

    outer = tk.Frame(dlg, background=BG, highlightthickness=1,
                     highlightbackground=BORDER_STRONG, highlightcolor=BORDER_STRONG)
    outer.pack(fill="both", expand=True)

    # Full-width application header.
    header = tk.Frame(outer, background=PRIMARY, height=122)
    header.pack(fill="x")
    header.pack_propagate(False)
    tk.Label(header, text="▤  Accounting App", background=PRIMARY,
             foreground=TEXT_INVERTED, font=("Segoe UI", 24, "bold")).pack(
                 anchor="center", pady=(23, SP2))
    tk.Label(header, text="Journal  •  Ledger  •  Balance Sheet", background=PRIMARY,
             foreground=BG_PANEL, font=("Segoe UI", 11)).pack(anchor="center")

    content = tk.Frame(outer, background=BG, padx=SP6, pady=SP4)
    content.pack(fill="both", expand=True)
    content.columnconfigure(0, weight=1, uniform="about_columns")
    content.columnconfigure(1, weight=0)
    content.columnconfigure(2, weight=1, uniform="about_columns")
    content.rowconfigure(0, weight=1)

    left = tk.Frame(content, background=BG_PANEL, padx=SP4, pady=SP4)
    left.grid(row=0, column=0, sticky="nsew")
    tk.Frame(content, background=BORDER, width=1).grid(row=0, column=1, sticky="ns", padx=SP4)
    right = tk.Frame(content, background=BG_PANEL, padx=SP4, pady=SP4)
    right.grid(row=0, column=2, sticky="nsew")

    def card_heading(parent, text):
        tk.Label(parent, text=text, background=BG_PANEL, foreground=TEXT,
                 font=("Segoe UI", 13, "bold"), anchor="w").pack(
                     anchor="w", fill="x", pady=(0, SP3))

    card_heading(left, "Developers")
    tk.Label(left, text="BSIT 2nd Year, 1st Semester - Group 3", background=BG_PANEL,
             foreground=TEXT, font=("Segoe UI", 11), anchor="w").pack(anchor="w", pady=(0, SP3))

    tk.Label(left, text="Group Leader", background=BG_PANEL, foreground=TEXT,
             font=("Segoe UI", 11, "bold"), anchor="w").pack(anchor="w", pady=(0, SP2))
    tk.Label(left, text="John Lourence C. Cabaluna", background=BG_PANEL, foreground=TEXT,
             font=("Segoe UI", 11), anchor="w").pack(anchor="w", pady=(0, SP3))

    tk.Label(left, text="Members", background=BG_PANEL, foreground=TEXT,
             font=("Segoe UI", 11, "bold"), anchor="w").pack(anchor="w", pady=(0, SP2))
    for name in ("Bea Marie Navaja", "Jau Rosal Huerte", "Angel Rizalyn Talledo",
                 "Ethan Vincent Vale", "Jeremy Binarao", "Robert M. Go", "Louie Jay Camaungay"):
        tk.Label(left, text=name, background=BG_PANEL, foreground=TEXT,
                 font=("Segoe UI", 11), anchor="w").pack(anchor="w", pady=(0, SP2))

    
    card_heading(right, "About the Application")
    description = (
        "The Accounting App is a desktop-based accounting system designed to help users "
        "record, organize, and manage financial transactions through an integrated accounting workflow."
    )
    description_label = tk.Label(right, text=description, background=BG_PANEL,
                                 foreground=TEXT, font=("Segoe UI", 11),
                                 justify="left", anchor="nw", wraplength=330)
    description_label.pack(anchor="w", fill="x")

    tk.Frame(right, background=BORDER, height=1).pack(fill="x", pady=(SP3, SP3))

    tk.Label(right, text="Key Features", background=BG_PANEL, foreground=TEXT,
             font=("Segoe UI", 13, "bold"), anchor="w").pack(
                 anchor="w", fill="x", pady=(0, SP3))
    features = (
        "Zero-setup core app. Excel and PDF export need openpyxl and reportlab.",
        "Complete accounting cycle: Journal → Ledger → 12-Column Worksheet.",
        "Automatic backups on every save (newest 20 kept).",
        "Data validation and corruption recovery with backup guidance.",
        "Edit entries by double-clicking in the Journal.",
        "Search and filter transactions instantly.",
        "Cached ledger for fast performance.",
        "Export to CSV, Excel (.xlsx), and PDF.",
    )
    feature_labels = []
    for feature in features:
        row = tk.Frame(right, background=BG_PANEL)
        row.pack(fill="x", anchor="w", pady=(0, SP2))
        tk.Label(row, text="✓", background=BG_PANEL, foreground=PRIMARY,
                 font=("Segoe UI", 10, "bold"), anchor="nw").pack(side="left", padx=(0, SP2))
        label = tk.Label(row, text=feature, background=BG_PANEL, foreground=TEXT,
                         font=("Segoe UI", 10), justify="left", anchor="nw",
                         wraplength=340)
        label.pack(side="left", fill="x", expand=True)
        feature_labels.append(label)

    # Keep text wrapping matched to the available column widths when resized.
    def resize_columns(_event=None):
        left_width = max(180, left.winfo_width() - 2 * SP4)
        right_width = max(180, right.winfo_width() - 2 * SP4 - 24)
        description_label.configure(wraplength=left_width)
        for label in feature_labels:
            label.configure(wraplength=right_width)

    content.bind("<Configure>", resize_columns, add="+")

    # Footer with the existing version and data-file information.
    footer = tk.Frame(outer, background=BG, padx=SP6, pady=SP3)
    footer.pack(fill="x")
    tk.Frame(footer, background=BORDER, height=1).pack(fill="x", pady=(0, SP3))
    footer_row = tk.Frame(footer, background=BG)
    footer_row.pack(fill="x")
    tk.Label(footer_row, text="Version 1.0 | Data saved to accounting_data.json",
             background=BG, foreground=TEXT_MUTED,
             font=("Segoe UI", 9), anchor="w").pack(side="left", anchor="center")

    close_canvas = tk.Canvas(footer_row, width=104, height=40, background=BG,
                             highlightthickness=0, bd=0, cursor="hand2", takefocus=True)
    close_canvas.pack(side="right")
    close_state = {"pressed": False}

    def draw_close(_event=None):
        close_canvas.delete("all")
        fill = "#1A3D8A" if close_state["pressed"] else PRIMARY_HOVER if close_canvas.winfo_containing(
            close_canvas.winfo_pointerx(), close_canvas.winfo_pointery()) is close_canvas else PRIMARY
        radius, width_px, height_px = 6, 104, 40
        points = []
        corners = (
            (width_px - radius - 1, radius + 1, -90, 0),
            (width_px - radius - 1, height_px - radius - 1, 0, 90),
            (radius + 1, height_px - radius - 1, 90, 180),
            (radius + 1, radius + 1, 180, 270),
        )
        for cx, cy, start, end in corners:
            for angle in range(start, end + 1, 15):
                radians = math.radians(angle)
                points.extend((cx + radius * math.cos(radians),
                               cy + radius * math.sin(radians)))
        close_canvas.create_polygon(*points, fill=fill, outline="")
        close_canvas.create_text(width_px / 2, height_px / 2, text="Close",
                                 font=("Segoe UI", 11, "bold"), fill=TEXT_INVERTED)

    def close_dialog(_event=None):
        dlg.destroy()

    def press_close(_event=None):
        close_state["pressed"] = True
        draw_close()

    def release_close(event=None):
        was_pressed = close_state["pressed"]
        close_state["pressed"] = False
        draw_close()
        if was_pressed and (event is None or 0 <= event.x <= 104 and 0 <= event.y <= 40):
            close_dialog()

    close_canvas.bind("<Enter>", draw_close)
    close_canvas.bind("<Leave>", draw_close)
    close_canvas.bind("<ButtonPress-1>", press_close)
    close_canvas.bind("<ButtonRelease-1>", release_close)
    close_canvas.bind("<KeyPress-space>", press_close)
    close_canvas.bind("<KeyRelease-space>", release_close)
    close_canvas.bind("<KeyPress-Return>", press_close)
    close_canvas.bind("<KeyRelease-Return>", release_close)
    draw_close()

    dlg.bind("<Escape>", close_dialog)
    dlg.protocol("WM_DELETE_WINDOW", close_dialog)
    # Keep resizable but open at proper content-fitted size
    dlg.update_idletasks()
    req_w = dlg.winfo_reqwidth()
    req_h = dlg.winfo_reqheight()
    actual_w = max(width, req_w + 40)  # At least design width + margin
    actual_h = max(520, req_h + 20)    # Minimum 520px ensures button fits
    x = root.winfo_rootx() + (root.winfo_width() - actual_w) // 2
    y = root.winfo_rooty() + (root.winfo_height() - actual_h) // 2
    dlg.geometry(f"{actual_w}x{actual_h}+{max(0, x)}+{max(0, y)}")
    dlg.grab_set()
    dlg.wait_window()

    