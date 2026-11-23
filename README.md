# Accounting_Group3

An offline desktop accounting app for **BSIT 2nd Year, 1st Semester, Group 3**. It teaches the accounting cycle:
you record journal entries, and the app builds the **Ledger** and a **12-column Worksheet** from them.
It is a teaching tool, not a production bookkeeping, tax or multi-user system.

## Features

- **Journal** - one debit account, one credit account and one amount per entry; add, edit, delete (one or many), search, adjusting-entry flag, custom accounts.
- **Ledger** - one account or all accounts with activity, grouped with subtotals (T-account style).
- **Worksheet** - Trial Balance, Adjustments, Adjusted Trial Balance, Income Statement, Owner's Equity and Balance Sheet columns, with Net Income/Loss and Ending Owner's Capital.
- **Export** - Journal, Ledger and Worksheet to CSV; Worksheet to Excel and PDF.
- **Safety** - automatic save after every change, timestamped backups (newest 20 kept, microsecond resolution prevents overwrites, no duplicate backups for identical saves), corrupted-file protection (unreadable.* files never deleted), Validate Data and Backup Manager in the Tools menu.

## Requirements

- Python 3.10 or newer with Tkinter (included with the standard Python installers on Windows and macOS).
- Nothing else is needed for core use. Optional: `pip install openpyxl` for Excel export and `pip install reportlab` for PDF export.

## Run

```
python main.py
```

## Your data

- Entries are saved automatically to `accounting_data.json`, next to `main.py`. A fresh copy of the project has no data file and starts empty.
- Before each save, the NEW data content is written as a backup to `accounting_data.backup.<timestamp>.json` (with microsecond resolution). Only the newest 20 are kept. Identical consecutive saves do not create duplicate backups. The newest backup normally equals the current data file; to go back one step, use the second newest backup. If the data file is corrupt on load, it is preserved as `accounting_data.unreadable.<timestamp>.json` and never deleted by the cleanup logic.
- To restore a backup, close the app and rename the backup file to `accounting_data.json`. The app has no restore button.
- The data file, backup files, unreadable files, temp file, and assistant tooling (.claude/) are all listed in `.gitignore` and will not be committed.

## Project layout

| File | Purpose |
|---|---|
| `main.py` | App window, menus, refresh, CSV exports, Validate Data, Backup Manager |
| `constants.py` | Account types, chart of accounts, number and date formatting |
| `data.py` | Loading, saving, backups, account lists |
| `journal_tab.py`, `journal_table.py` | Journal form and table |
| `ledger_tab.py` | Ledger screen |
| `worksheet_tab.py`, `grid_table.py` | 12-column Worksheet and exports |
| `style.py`, `about_tab.py` | Look and feel, About dialog |

## More documentation

`PRODUCT.md` (what the app does), `ARCHITECTURE.md` (how it is built and known issues), `DESIGN.md` (visual rules),
`MEMORY.md` (current state and decisions), `AI_GUIDE.md` (rules for AI assistants and developers), `SESSION_HANDOFF.md` (latest status).
