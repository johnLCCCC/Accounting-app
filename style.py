"""Look and feel: ttk styles — Clean Minimalist Accounting App design system."""
from tkinter import ttk

# ─── Design Tokens ────────────────────────────────────────────────────────

# Colors (Light mode — Clean Minimalist Blue)
COLOR_BG = "#F3F7FC"
COLOR_BG_ALT = "#EAF2FB"
COLOR_BG_PANEL = "#EAF2FB"
COLOR_BORDER = "#D5E1EE"
COLOR_BORDER_STRONG = "#D5E1EE"
COLOR_TEXT = "#344B63"
COLOR_TEXT_MUTED = "#60778F"
COLOR_TEXT_INVERTED = "#F8FBFF"

COLOR_PRIMARY = "#397DC1"
COLOR_PRIMARY_HOVER = "#4B88C5"
COLOR_PRIMARY_LIGHT = "#DCE9F7"
COLOR_PRIMARY_FOCUS = "#D5E1EE"

COLOR_SUCCESS = "#397DC1"
COLOR_SUCCESS_LIGHT = "#EAF2FB"
COLOR_DANGER = "#397DC1"
COLOR_DANGER_LIGHT = "#EAF2FB"
COLOR_WARNING = "#397DC1"
COLOR_WARNING_LIGHT = "#D9ECFF"

COLOR_ACCENT = "#397DC1"
COLOR_ACCENT_HOVER = "#4B88C5"
COLOR_ACCENT_PRESSED = "#4B88C5"
COLOR_ACCENT_LIGHT = "#EAF2FB"

# Spacing (base 4px) — Compact but comfortable (between current and team version)
SPACE_1 = 4
SPACE_2 = 6      # Was 8
SPACE_3 = 10     # Was 12
SPACE_4 = 14     # Was 16
SPACE_5 = 16     # Was 20
SPACE_6 = 18     # Was 24
SPACE_8 = 24     # Was 32

# Typography — slightly larger scale for readability (from team version)
FONT_UI = "Segoe UI"

TEXT_XS = (FONT_UI, 11)        # Was 10
TEXT_SM = (FONT_UI, 12)        # Was 11
TEXT_SM_BOLD = (FONT_UI, 12, "bold")  # For worksheet totals — subtle emphasis
TEXT_BASE = (FONT_UI, 14)      # Was 12
TEXT_LG = (FONT_UI, 16, "bold")   # Was 13
TEXT_XL = (FONT_UI, 18, "bold")   # Was 15
TEXT_2XL = (FONT_UI, 22, "bold")  # Was 18

# Table
TABLE_ROW_HEIGHT = 28
TABLE_HEADER_HEIGHT = 32

# Aliases for grid_table.py
ROW_H = TABLE_ROW_HEIGHT
HEAD_H = TABLE_HEADER_HEIGHT

# Aliases for backward compatibility with tabs
F_XS = TEXT_XS
F_SM = TEXT_SM
F_SM_BOLD = TEXT_SM_BOLD
F_BASE = TEXT_BASE
F_BOLD = TEXT_LG
F_MONO = ("Consolas", 12)

SP1 = SPACE_1
SP2 = SPACE_2
SP3 = SPACE_3
SP4 = SPACE_4
SP5 = SPACE_5
SP6 = SPACE_6
SP8 = SPACE_8

# Color aliases
BG = COLOR_BG
BG_ALT = COLOR_BG_ALT
BG_PANEL = COLOR_BG
BORDER = COLOR_BORDER
BORDER_STRONG = COLOR_BORDER_STRONG
TEXT = COLOR_TEXT
TEXT_MUTED = COLOR_TEXT_MUTED
TEXT_INVERTED = COLOR_TEXT_INVERTED
PRIMARY = COLOR_PRIMARY
PRIMARY_LIGHT = COLOR_PRIMARY_LIGHT
PRIMARY_HOVER = COLOR_PRIMARY_HOVER
PRIMARY_FOCUS = COLOR_PRIMARY_FOCUS
WARNING = COLOR_WARNING
WARNING_LIGHT = COLOR_WARNING_LIGHT

# Accent aliases
ACCENT = COLOR_ACCENT
ACCENT_HOVER = COLOR_ACCENT_HOVER
ACCENT_PRESSED = COLOR_ACCENT_PRESSED
ACCENT_LIGHT = COLOR_ACCENT_LIGHT

# Helper function for journal_tab.py
def fmt_amt(v):
    """Format amount for display."""
    from constants import ZERO
    from decimal import Decimal
    if v is None or v == ZERO or v == 0:
        return ""
    v = Decimal(str(v))
    return f"{v:,.0f}" if v == v.to_integral_value() else f"{v:,.2f}"


# ─── Style Mixin ──────────────────────────────────────────────────────────

class StyleMixin:
    """Applies a clean, minimalist ttk theme."""

    def set_style(self):
        s = ttk.Style()
        s.theme_use("clam")

        # Base font
        s.configure(".", font=TEXT_BASE)

        # ─── Treeview (Table) ──────────────────────────────────────────
        s.configure(
            "Treeview",
            rowheight=TABLE_ROW_HEIGHT,
            background=COLOR_BG_ALT,
            fieldbackground=COLOR_BG_ALT,
            borderwidth=0,
            relief="flat",
            font=TEXT_SM,
        )
        s.configure(
            "Treeview.Heading",
            background="#DCEAF8",
            foreground=COLOR_TEXT_INVERTED,
            font=(FONT_UI, 12, "bold"),  # Was 11
            relief="flat",
            padding=(SPACE_3, SPACE_2),
            borderwidth=(0, 0, 1, 0),
        )
        s.map("Treeview.Heading", background=[("active", COLOR_PRIMARY_HOVER)])

        # Ledger-only heading styling to match the Journal table header.
        s.layout("Ledger.Treeview", s.layout("Treeview"))
        s.configure(
            "Ledger.Treeview",
            rowheight=TABLE_ROW_HEIGHT,
            background=COLOR_BG_ALT,
            fieldbackground=COLOR_BG_ALT,
            borderwidth=0,
            relief="flat",
            font=TEXT_SM,
        )
        s.map(
            "Ledger.Treeview",
            background=[("selected", COLOR_PRIMARY_LIGHT)],
            foreground=[("selected", COLOR_PRIMARY)],
        )
        s.configure(
            "Ledger.Treeview.Heading",
            background=PRIMARY,
            foreground="#FFFFFF",
            font=(FONT_UI, 12, "bold"),
            relief="flat",
            padding=(SPACE_3, SPACE_2),
            borderwidth=(0, 0, 1, 0),
        )
        s.map("Ledger.Treeview.Heading", background=[("active", PRIMARY_HOVER)])

        # Row selection - subtle blue highlight
        s.map(
            "Treeview",
            background=[("selected", COLOR_PRIMARY_LIGHT)],
            foreground=[("selected", COLOR_PRIMARY)],
        )

        # Striped rows via tags (applied in code)
        # .odd tag for alternating rows

        # ─── Buttons ───────────────────────────────────────────────────
        s.configure(
            "TButton",
            padding=(SPACE_3, SPACE_2),
            font=(FONT_UI, 12),  # Was 11
            borderwidth=1,
            relief="flat",
        )
        s.map("TButton",
            background=[("active", COLOR_BG_ALT), ("pressed", COLOR_BORDER)],
            relief=[("pressed", "sunken"), ("!pressed", "flat")],
        )

        s.configure(
            "Primary.TButton",
            background=COLOR_PRIMARY,
            foreground=COLOR_TEXT_INVERTED,
            font=(FONT_UI, 12, "bold"),  # Was 11
            borderwidth=1,
            padding=(SPACE_4, SPACE_2),
        )
        s.map("Primary.TButton",
            background=[("active", COLOR_PRIMARY_HOVER), ("pressed", COLOR_PRIMARY_HOVER)],
            bordercolor=[("active", COLOR_PRIMARY_HOVER), ("pressed", COLOR_PRIMARY_HOVER), ("!active", COLOR_PRIMARY)],
            relief=[("pressed", "flat"), ("!pressed", "flat")],
        )

        s.configure(
            "Ghost.TButton",
            background="#F8FBFF",
            foreground=COLOR_TEXT,
            font=(FONT_UI, 12),  # Was 11
            borderwidth=1,
            padding=(SPACE_3, SPACE_2),
        )
        s.map("Ghost.TButton",
            background=[("active", COLOR_BG_ALT), ("pressed", COLOR_BORDER)],
            bordercolor=[("active", COLOR_BORDER_STRONG)],
        )

        s.configure(
            "Danger.TButton",
            background=COLOR_PRIMARY,
            foreground=COLOR_TEXT_INVERTED,
            font=(FONT_UI, 12, "bold"),  # Was 11
            borderwidth=0,
            padding=(SPACE_3, SPACE_2),
        )
        s.map("Danger.TButton",
            background=[("active", COLOR_PRIMARY_HOVER), ("pressed", COLOR_PRIMARY_HOVER)],
        )

        # ─── Combobox ──────────────────────────────────────────────────
        s.configure(
            "TCombobox",
            padding=(SPACE_2, SPACE_1),
            font=TEXT_BASE,  # Was TEXT_SM
            fieldbackground="#F8FBFF",
            background="#F8FBFF",
            borderwidth=1,
            relief="flat",
        )
        s.map("TCombobox",
            fieldbackground=[("readonly", "#F8FBFF"), ("focus", "#F8FBFF")],
            bordercolor=[("focus", COLOR_PRIMARY)],
            lightcolor=[("focus", COLOR_PRIMARY)],
            darkcolor=[("focus", COLOR_PRIMARY)],
        )
        self.root.option_add("*TCombobox*Listbox.font", TEXT_SM)
        self.root.option_add("*TCombobox*Listbox.background", "#F8FBFF")
        self.root.option_add("*TCombobox*Listbox.foreground", COLOR_TEXT)
        self.root.option_add("*TCombobox*Listbox.selectBackground", COLOR_PRIMARY_LIGHT)
        self.root.option_add("*TCombobox*Listbox.selectForeground", COLOR_PRIMARY)

        # Custom LedgerFilter combobox style (from team version)
        s.configure(
            "LedgerFilter.TCombobox",
            font=(FONT_UI, 12),
            padding=(10, 10),
            bordercolor=BORDER_STRONG,
        )
        s.map(
            "LedgerFilter.TCombobox",
            bordercolor=[("focus", PRIMARY), ("!focus", BORDER_STRONG)],
        )

        # ─── Entry ─────────────────────────────────────────────────────
        s.configure(
            "TEntry",
            padding=(SPACE_2, SPACE_1),
            font=TEXT_BASE,  # Was TEXT_SM
            fieldbackground="#F8FBFF",
            borderwidth=1,
            relief="flat",
        )
        s.map("TEntry",
            bordercolor=[("focus", COLOR_PRIMARY)],
            lightcolor=[("focus", COLOR_PRIMARY)],
            darkcolor=[("focus", COLOR_PRIMARY)],
        )

        # ─── Notebook (Tabs) ──────────────────────────────────────────
        s.configure(
            "TNotebook",
            background=COLOR_BG_PANEL,  # Match Panel.TFrame for seamless tab area
            borderwidth=0,
            tabmargins=(0, 0, 0, 0),
        )
        s.configure(
            "TNotebook.Tab",
            padding=(SPACE_5, SPACE_3),
            font=(FONT_UI, 12, "bold"),  # Was 11
            background="#DCE9F7",
            foreground=COLOR_TEXT_MUTED,
            borderwidth=0,
        )
        s.map("TNotebook.Tab",
            background=[("selected", "#F8FBFF"), ("active", COLOR_BG_ALT)],
            foreground=[("selected", COLOR_PRIMARY), ("active", COLOR_TEXT)],
        )

        # ─── Frames ────────────────────────────────────────────────────
        s.configure(
            "Card.TFrame",
            background=COLOR_BG_PANEL,
            borderwidth=1,
            relief="solid",
        )
        s.map("Card.TFrame", background=[("", COLOR_BORDER)])

        s.configure(
            "Panel.TFrame",
            background=COLOR_BG_PANEL,
            borderwidth=0,
            relief="flat",
        )

        s.configure(
            "Section.TLabelframe",
            background=COLOR_BG_PANEL,
            borderwidth=1,
            relief="solid",
            font=(FONT_UI, 11, "bold"),
            foreground=COLOR_TEXT,
        )
        s.configure(
            "Section.TLabelframe.Label",
            background=COLOR_BG_PANEL,
            foreground=COLOR_TEXT,
            font=(FONT_UI, 11, "bold"),
            padding=(SPACE_2, 0, SPACE_2, SPACE_1),
        )

        # ─── Scrollbar ─────────────────────────────────────────────────
        s.configure(
            "Vertical.TScrollbar",
            background=COLOR_BG_ALT,
            troughcolor=COLOR_BG,
            borderwidth=0,
            arrowsize=10,
            width=10,
        )
        s.map("Vertical.TScrollbar",
            background=[("active", COLOR_BORDER_STRONG), ("pressed", COLOR_BORDER)],
        )

        s.configure(
            "Horizontal.TScrollbar",
            background=COLOR_BG_ALT,
            troughcolor=COLOR_BG,
            borderwidth=0,
            arrowsize=10,
            height=10,
        )
        s.map("Horizontal.TScrollbar",
            background=[("active", COLOR_BORDER_STRONG), ("pressed", COLOR_BORDER)],
        )

        # ─── Labels ────────────────────────────────────────────────────
        s.configure("TLabel", background=COLOR_BG_PANEL, foreground=COLOR_TEXT, font=TEXT_BASE)
        s.configure("Muted.TLabel", foreground=COLOR_TEXT, font=TEXT_SM, background=COLOR_BG_PANEL)
        s.configure("Title.TLabel", font=TEXT_2XL, foreground=COLOR_TEXT, background=COLOR_BG_PANEL)
        s.configure("Subtitle.TLabel", font=TEXT_LG, foreground=COLOR_TEXT_MUTED, background=COLOR_BG_PANEL)
        s.configure("Heading.TLabel", font=TEXT_LG, foreground=COLOR_TEXT)
        s.configure("FieldLabel.TLabel", font=TEXT_SM, foreground=COLOR_TEXT, background=COLOR_BG_PANEL)
        s.configure("Counter.TLabel", background=COLOR_BG_PANEL, foreground=ACCENT,
                    font=(FONT_UI, 11, "bold"), padding=(SPACE_3, SPACE_1))
        s.configure("Error.TLabel", foreground=COLOR_DANGER, font=TEXT_SM)
        s.configure("Success.TLabel", foreground=COLOR_SUCCESS, font=TEXT_SM)

        # Validation styles
        s.configure("Error.TEntry", fieldbackground=COLOR_DANGER_LIGHT)
        s.configure("Error.TCombobox", fieldbackground=COLOR_DANGER_LIGHT)

        # Worksheet export button style (from team version) — now uses accent teal
        s.configure(
            "WorksheetExport.TButton",
            background=ACCENT,
            foreground=TEXT_INVERTED,
            font=(FONT_UI, 11, "bold"),
            borderwidth=1,
            relief="flat",
            padding=(12, 9),
            focusthickness=0,
        )
        s.map("WorksheetExport.TButton",
              background=[("pressed", ACCENT_PRESSED), ("active", ACCENT_HOVER)],
              bordercolor=[("active", ACCENT_HOVER), ("pressed", ACCENT_PRESSED), ("!active", ACCENT)])

    # ─── Treeview Builder ────────────────────────────────────────────────

    def make_tree(self, parent, cols, heads, widths, left=(), show="headings", hscroll=False):
        """
        Create a styled Treeview inside a card container.
        Returns the Treeview widget.
        """
        box = ttk.Frame(parent, style="Card.TFrame", padding=0)
        box.pack(fill="both", expand=True)

        inner = ttk.Frame(box, style="Card.TFrame")
        inner.pack(fill="both", expand=True, padx=1, pady=1)

        t = ttk.Treeview(inner, columns=cols, show=show, selectmode="browse", style="Treeview")
        for c, h, w in zip(cols, heads, widths):
            a = "w" if c in left else "e"
            t.heading(c, text=h, anchor=a)
            t.column(c, width=w, minwidth=60, anchor=a, stretch=c in left)

        ys = ttk.Scrollbar(inner, command=t.yview, style="Vertical.TScrollbar")
        t.configure(yscrollcommand=ys.set)
        ys.pack(side="right", fill="y")

        if hscroll:
            xs = ttk.Scrollbar(inner, orient="horizontal", command=t.xview, style="Horizontal.TScrollbar")
            t.configure(xscrollcommand=xs.set)
            xs.pack(side="bottom", fill="x")

        t.pack(side="left", fill="both", expand=True)

        # Configure row tags for this specific tree
        self._configure_tree_tags(t)

        return t

    def _configure_tree_tags(self, tree):
        """Configure all semantic row tags for a tree."""
        tree.tag_configure("odd", background=COLOR_BG_ALT)
        tree.tag_configure("adj", background=COLOR_WARNING_LIGHT)
        tree.tag_configure("total",
            background=COLOR_BG_ALT,
            font=(FONT_UI, 10, "bold"),
            foreground=COLOR_TEXT,
        )
        tree.tag_configure("grand",
            background=COLOR_PRIMARY_LIGHT,
            font=(FONT_UI, 10, "bold"),
            foreground=COLOR_PRIMARY,
        )
        tree.tag_configure("empty",
            foreground=COLOR_TEXT_MUTED,
            font=(FONT_UI, 11, "italic"),
        )
        tree.tag_configure("acct",
            background=ACCENT_LIGHT,
            font=(FONT_UI, 11, "bold"),
            foreground=ACCENT_HOVER,
        )
        tree.tag_configure("credit_line", font=TEXT_SM)
        tree.tag_configure("desc_line", foreground=COLOR_TEXT_MUTED, font=(FONT_UI, 10, "italic"))
