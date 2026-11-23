"""Tab 3: Worksheet / Balance Sheet screen — Clean Minimalist redesign."""
import csv
from decimal import Decimal
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from constants import HEADS, SECTION, SECTION_COL, ZERO, fmt
from grid_table import GridTable
from style import (
    BG_PANEL, PRIMARY, PRIMARY_LIGHT, PRIMARY_HOVER,
    BORDER_STRONG,
    SP2, SP3, SP4, SP6,
)


# titles shown above each Dr/Cr pair (same order as the HEADS columns)
GROUP_TITLES = ["Trial Balance", "Adjustments", "Adjusted Trial Balance",
                "Income Statement", "Owner's Equity", "Balance Sheet"]


class WorksheetMixin:
    def build_worksheet(self, nb):
        tab = ttk.Frame(nb, style="Panel.TFrame")
        nb.add(tab, text="▦  Worksheet")

        # ─── Export Bar ──────────────────────────────────────────────
        top = ttk.Frame(tab, style="Panel.TFrame", padding=(SP6, SP4))
        top.pack(fill="x", padx=SP6, pady=(SP6, SP4))

        # Title on the left (team version pattern)
        ttk.Label(top, text="Worksheet", style="Title.TLabel", background=BG_PANEL).pack(side="left")

        # Export buttons on the right (team version pattern)
        exports = ttk.Frame(top, style="Panel.TFrame")
        exports.pack(side="right")
        btn_csv = ttk.Button(exports, text="Export CSV", style="WorksheetExport.TButton",
                   command=self.export_worksheet_csv)
        btn_csv.pack(side="left", padx=(0, SP3))
        btn_excel = ttk.Button(exports, text="Export Excel", style="WorksheetExport.TButton",
                   command=self.export_excel)
        btn_excel.pack(side="left", padx=(0, SP3))
        btn_pdf = ttk.Button(exports, text="Export PDF", style="WorksheetExport.TButton",
                   command=self.export_pdf)
        btn_pdf.pack(side="left")
        # Hover effect for WorksheetExport.TButton
        for btn in (btn_csv, btn_excel, btn_pdf):
            btn.bind("<Enter>", lambda e: e.widget.state(["active"]))
            btn.bind("<Leave>", lambda e: e.widget.state(["!active"]))

        # Thin separator between export bar and worksheet table (team version pattern)
        tk.Frame(tab, height=1, background=BORDER_STRONG, bd=0, highlightthickness=0).pack(fill="x", padx=SP6)

        # ─── Worksheet Table ────────────────────────────────────────
        self.wt = GridTable(tab, "Account Name", GROUP_TITLES)
        self.wt.pack(fill="both", expand=True, padx=SP4, pady=(SP3, SP6))

    def compute_worksheet(self):
        types, names = self.types(), self.get_all_account_names()
        tb = {n: [ZERO, ZERO] for n in names}
        adj = {n: [ZERO, ZERO] for n in names}
        for e in self.entries:
            a = Decimal(e["amount"])
            t = adj if e["adj"] else tb
            t[e["debit"]][0] += a
            t[e["credit"]][1] += a

        def split(x):  # net balance -> (Dr, Cr)
            return (x, None) if x > 0 else (None, -x) if x < 0 else (None, None)

        rows = []
        for i, n in enumerate(names):
            tnet = tb[n][0] - tb[n][1]
            anet = tnet + adj[n][0] - adj[n][1]
            c = [None] * 12
            c[0], c[1] = split(tnet)
            c[2], c[3] = adj[n][0] or None, adj[n][1] or None
            c[4], c[5] = split(anet)
            k = SECTION_COL[SECTION[types[n]]]
            c[k], c[k + 1] = c[4], c[5]
            rows.append((n, c, "odd" if i % 2 else ""))

        total = [sum((r[1][j] or ZERO for r in rows), ZERO) for j in range(12)]
        rows.append(("TOTAL", total, "total"))

        ni = total[7] - total[6]  # revenue - expenses
        ni_row = [None] * 12
        if ni >= 0:
            ni_row[6] = ni_row[9] = ni
        else:
            ni_row[7] = ni_row[8] = -ni
        rows.append(("NET INCOME" if ni >= 0 else "NET LOSS", ni_row, "total"))

        ec = (total[9] + (ni_row[9] or ZERO)) - (total[8] + (ni_row[8] or ZERO))
        ec_row = [None] * 12
        if ec >= 0:
            ec_row[8] = ec_row[11] = ec
        else:
            ec_row[9] = ec_row[10] = -ec
        rows.append(("ENDING OWNER'S CAPITAL", ec_row, "total"))

        grand = [None] * 6 + [sum((r[j] or ZERO for r in (total, ni_row, ec_row)), ZERO) for j in range(6, 12)]
        rows.append(("GRAND TOTAL", grand, "grand"))
        ok = {"TB": total[0] == total[1], "ADJ": total[2] == total[3], "ATB": total[4] == total[5],
              "IS": grand[6] == grand[7], "OE": grand[8] == grand[9], "BS": grand[10] == grand[11]}
        return rows, ok

    def export_worksheet_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", initialfile="worksheet.csv",
                                            filetypes=[("CSV file", "*.csv")])
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(["Account Name"] + HEADS)
            for name, cells, _ in self.ws_rows:
                w.writerow([name] + [fmt(c) for c in cells])
        messagebox.showinfo("Export", "Worksheet exported.")

    def export_excel(self):
        """Export worksheet to Excel with formatting and formulas."""
        try:
            from openpyxl import Workbook
            from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
            from openpyxl.utils import get_column_letter
        except ImportError:
            messagebox.showerror(
                "Missing Library",
                "Excel export requires the 'openpyxl' library.\n\n"
                "Install it with: pip install openpyxl"
            )
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            initialfile="worksheet.xlsx",
            filetypes=[("Excel file", "*.xlsx")]
        )
        if not path:
            return

        try:
            wb = Workbook()
            ws = wb.active
            ws.title = "Worksheet"

            # Styles
            header_font = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
            header_fill = PatternFill(start_color="2563EB", end_color="2563EB", fill_type="solid")
            title_font = Font(name="Segoe UI", size=14, bold=True)
            total_font = Font(name="Segoe UI", size=11, bold=True)
            total_fill = PatternFill(start_color="DBEAFE", end_color="DBEAFE", fill_type="solid")
            thin_border = Border(
                left=Side(style='thin', color='E2E8F0'),
                right=Side(style='thin', color='E2E8F0'),
                top=Side(style='thin', color='E2E8F0'),
                bottom=Side(style='thin', color='E2E8F0')
            )
            center_align = Alignment(horizontal="center", vertical="center")
            right_align = Alignment(horizontal="right", vertical="center")
            left_align = Alignment(horizontal="left", vertical="center")

            # Title
            ws.merge_cells("A1:M1")
            ws["A1"] = "12-Column Worksheet"
            ws["A1"].font = title_font
            ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
            ws.row_dimensions[1].height = 25

            # Column headers
            headers = ["Account Name"] + HEADS
            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=3, column=col)
                cell.value = header
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = center_align
                cell.border = thin_border
            ws.row_dimensions[3].height = 20

            # Data rows
            row_num = 4
            for name, cells, tag in self.ws_rows:
                ws.cell(row=row_num, column=1, value=name).alignment = left_align
                for col, val in enumerate(cells, 2):
                    cell = ws.cell(row=row_num, column=col)
                    if val is not None:
                        cell.value = float(val)
                        cell.number_format = '#,##0.00'
                        cell.alignment = right_align
                    else:
                        cell.alignment = center_align
                ws.row_dimensions[row_num].height = 18

                # Apply formatting for total/grand rows
                if tag in ("total", "grand"):
                    for col in range(1, len(headers) + 1):
                        cell = ws.cell(row=row_num, column=col)
                        cell.font = total_font
                        if tag == "grand":
                            cell.fill = total_fill
                        cell.border = thin_border
                else:
                    for col in range(1, len(headers) + 1):
                        ws.cell(row=row_num, column=col).border = thin_border

                row_num += 1

            # Auto-fit columns
            for col in range(1, len(headers) + 1):
                col_letter = get_column_letter(col)
                if col == 1:
                    ws.column_dimensions[col_letter].width = 28
                else:
                    ws.column_dimensions[col_letter].width = 14

            # Freeze panes (header row)
            ws.freeze_panes = "A4"

            wb.save(path)
            messagebox.showinfo(
                "Export Successful",
                f"Worksheet exported to Excel:\n{path}\n\n"
                "Features included:\n"
                "• Formatted headers with colors\n"
                "• Currency formatting\n"
                "• Auto-sized columns\n"
                "• Frozen header row"
            )
        except Exception as err:
            messagebox.showerror(
                "Export Failed",
                f"Could not export to Excel:\n{err}\n\n"
                "Please check that you have write access to the selected location."
            )

    def export_pdf(self):
        """Export worksheet as a professional PDF document."""
        try:
            from reportlab.lib.pagesizes import letter, landscape
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors
        except ImportError:
            messagebox.showerror(
                "Missing Library",
                "PDF export requires the 'reportlab' library.\n\n"
                "Install it with: pip install reportlab"
            )
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            initialfile="worksheet.pdf",
            filetypes=[("PDF file", "*.pdf")]
        )
        if not path:
            return

        try:
            # Setup PDF in landscape mode (12 columns need width)
            doc = SimpleDocTemplate(
                path,
                pagesize=landscape(letter),
                rightMargin=20,
                leftMargin=20,
                topMargin=20,
                bottomMargin=20
            )

            elements = []
            styles = getSampleStyleSheet()

            # Title & Subtitle
            title_style = ParagraphStyle(
                'DocTitle',
                parent=styles['Heading1'],
                fontSize=18,
                leading=22,
                textColor=colors.HexColor('#2563EB'),
                alignment=1,  # Center
                spaceAfter=6
            )
            subtitle_style = ParagraphStyle(
                'DocSubtitle',
                parent=styles['Normal'],
                fontSize=10,
                leading=12,
                textColor=colors.HexColor('#64748B'),
                alignment=1,  # Center
                spaceAfter=12
            )

            elements.append(Paragraph("Accounting 12-Column Worksheet", title_style))
            elements.append(Paragraph("Trial Balance | Adjustments | Income Statement | Balance Sheet", subtitle_style))

            # Table Header Data
            table_data = [
                ["Account Name"] + HEADS
            ]

            # Table Row Data
            for name, cells, _ in self.ws_rows:
                row = [name] + [fmt(c) for c in cells]
                table_data.append(row)

            # Column Widths (total ~750 points for landscape letter page)
            col_widths = [110] + [52] * 12

            # Table Style
            table_style = TableStyle([
                # Header formatting
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563EB')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 7),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 4),
                ('TOPPADDING', (0, 0), (-1, 0), 4),

                # Grid lines
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),

                # Alignment
                ('ALIGN', (0, 1), (0, -1), 'LEFT'),      # Account names left
                ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),    # Numbers right

                # Fonts
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 6.5),
                ('TOPPADDING', (0, 1), (-1, -1), 2),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 2),
            ])

            # Apply row-specific styles (totals and grand totals)
            for idx, (name, _, tag) in enumerate(self.ws_rows, start=1):
                if tag == "grand":
                    table_style.add('BACKGROUND', (0, idx), (-1, idx), colors.HexColor('#DBEAFE'))
                    table_style.add('FONTNAME', (0, idx), (-1, idx), 'Helvetica-Bold')
                    table_style.add('LINEABOVE', (0, idx), (-1, idx), 1, colors.HexColor('#2563EB'))
                    table_style.add('LINEBELOW', (0, idx), (-1, idx), 2, colors.HexColor('#2563EB'))
                elif tag == "total":
                    table_style.add('FONTNAME', (0, idx), (-1, idx), 'Helvetica-Bold')
                    table_style.add('LINEABOVE', (0, idx), (-1, idx), 0.5, colors.black)

            t = Table(table_data, colWidths=col_widths, repeatRows=1)
            t.setStyle(table_style)
            elements.append(t)

            doc.build(elements)

            messagebox.showinfo(
                "Export Successful",
                f"Worksheet exported to PDF:\n{path}\n\n"
                "Features included:\n"
                "• Professional landscape layout\n"
                "• Formatted accounting tables\n"
                "• Repeated headers on multi-page export\n"
                "• Highlighted totals and grand totals"
            )
        except Exception as err:
            messagebox.showerror(
                "Export Failed",
                f"Could not export to PDF:\n{err}\n\n"
                "Please check that reportlab is installed and you have write permissions."
            )

    def refresh_worksheet(self):
        rows, _ = self.compute_worksheet()
        self.ws_rows = rows
        self.wt.set_rows([(name, [fmt(c) for c in cells], tag) for name, cells, tag in rows])