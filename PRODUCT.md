# Product

> **Purpose:** This document describes what the Accounting App is for, who uses it, what it can and cannot do today,
> and which product decisions are already made. It is written for developers and AI assistants deciding whether a change
> fits the product.
>
> **Authority:** It records the *current, verified* product. The source code is the final authority on behavior;
> `ARCHITECTURE.md` explains how things work internally; `DESIGN.md` covers the look and feel; `AI_GUIDE.md` covers working rules.
> If this document and the code disagree, check the code, then correct this file. Do not assume either is right.
>
> **Status labels** used in §4:
> **Works (tested)** = reproduced by running the code with Tkinter stubbed and synthetic data;
> **Works (read)** = established by reading the code, GUI not launched;
> **Defect** = known not to work as intended;
> **Not run** = exists in code but was not executed during review.

---

## 1. Product Summary

Accounting App is a zero-setup, offline desktop learning tool for BSIT students completing accounting assignments.
A student records a journal entry once and sees its effects in the **Ledger** and the **12-column Worksheet**.

It is a teaching tool for the accounting cycle, not a production bookkeeping, tax, or multi-user system.

## 2. Users and Context

- **Primary users:** BSIT 2nd Year, 1st Semester students (Group 3's class project) learning the accounting cycle.
- **Typical use:** enter a classroom exercise, check the ledger and worksheet totals, then export the worksheet to submit.
- **Environment:** Windows is the main target (Segoe UI / Consolas fonts, window starts maximized on Windows).
  The app has not been checked on other operating systems.
- **Setup:** `python main.py`. Core use needs only Python 3.10+ and the standard library (Tkinter).
  Excel export needs `openpyxl`; PDF export needs `reportlab`.
- **Connectivity:** none. Data is saved in `accounting_data.json` beside the program.

## 3. Core Student Workflow

1. **Record** a journal entry: date, debit account, credit account, amount, description, and whether it is an *Adjusting Entry*.
2. **Review** the entry in the Journal table (search, edit, or delete if needed).
3. **Check the Ledger:** pick one account, or "All Accounts", and see its postings and totals.
4. **Check the Worksheet:** read the 12 columns from Trial Balance to Balance Sheet, plus Net Income/Net Loss and Ending Owner's Capital.
5. **Export** the result (see §4 for which exports currently work).

Every screen after the Journal is **derived** from the Journal; students never type directly into the Ledger or Worksheet.

## 4. Current Capabilities

| Capability | What a student can do | Status |
|---|---|---|
| Journal entry form | Pick date by month/day/year dropdowns (years from 10 back to 5 ahead); pick debit and credit accounts with type-ahead filtering; enter an amount (commas, `₱`, `$` are accepted and ignored); add a description; tick *Adjusting Entry*. Fields start locked and unlock on click (intentional). | Works (read) |
| Input validation | Rejects an invalid date, missing accounts, same debit and credit account, and amounts that are not positive numbers. Amounts are stored with 2 decimals. | Works (read) |
| Default description | A blank description is saved as an empty string `""` (previously `[wala ni enter ug description]`, fixed 2026-11-21). Old entries with the placeholder are preserved unchanged. | Works (tested) |
| Chart of accounts | 27 predefined accounts in six types. Typing a new name opens a prompt to choose its type; the new account then appears in the dropdowns. | Works (read); typing-and-cleanup logic tested |
| Custom account lifecycle | A custom account stays only while an entry uses it; after its last entry is deleted it disappears. | Works (tested logic); dropdown behavior needs manual check |
| Search | Filters the Journal by account name, description, date, or amount; shows "x of y entries". | Works (read) |
| Edit | Double-click an entry, change it, choose *Update Entry* or *Cancel*. | Works (read) |
| Delete | Delete one entry (form button, Edit > Delete Entry) or several (checkbox selection mode, Delete key when the table has focus), always after a confirmation. | Works (read) |
| Right-click menu on a Journal row | Intended to offer Edit/Delete. | Works (read) — **FIXED** (now created in `build_journal`) |
| Ledger | One account, or all accounts that have activity grouped with a subtotal each. Shows date, explanation, Dr, Cr. Adjusting entries are tinted and marked `[Adj]`. | Works (tested math, read display) |
| Ledger balance | The balance appears on each account's **Subtotal / TOTALS row** (e.g. `1,000 Dr`). Individual rows do **not** show a running balance on screen — **intentional** (follows instructor's T-account format). | Works as described |
| 12-column Worksheet | Trial Balance, Adjustments, Adjusted Trial Balance, Income Statement, Owner's Equity, Balance Sheet, with TOTAL, NET INCOME/NET LOSS, ENDING OWNER'S CAPITAL, and GRAND TOTAL rows. | Works (tested) |
| Worksheet balance status | The totals are computed and balanced in all tested cases, but the app shows **no "balanced / not balanced" indicator**. A student must compare the Dr and Cr totals by eye. | Gap (see §8) |
| Automatic save and backups | Every add, edit, or delete saves immediately. The NEW data content is written as a timestamped backup (microsecond resolution, counter suffix if needed); the newest 20 backups are kept. Identical consecutive saves skip backup creation. The newest backup equals the current data file; to go back one step, use the second newest. If the data file is corrupt on load, it is preserved as `accounting_data.unreadable.<timestamp>.json` and never deleted. | Works (tested); see §8 #8-#9 |
| Journal CSV export | Date, accounts, amount, description, adjusting flag. | Works (read) |
| Ledger CSV export | Follows the selected Ledger account; includes a running balance per line. | Works (read) |
| **Worksheet CSV export** | From the Worksheet tab (button or File > Export > Export CSV). | Works (read) — **FIXED** (recursion resolved in `main.py`) |
| Excel / PDF export | Worksheet only, from the menu or the Worksheet tab. Shows an install message if the package is missing. | Not run |
| Tools menu | *Validate Data* reports bad entries; *Backup Manager* lists backup file names (it cannot restore). | Works (read) |
| Help menu | Keyboard Shortcuts dialog and About dialog. | Works (read) |

## 5. Accounting Scope

**Modeled:**
- Six account types: Asset, Liability, Owner's Capital, Owner's Drawings, Revenue, Expense. Each type decides which statement columns an account lands in.
- Entries are a **single debit/credit pair**; entries marked adjusting appear in the Adjustments columns, others in Trial Balance.
- Net income or net loss and ending owner's capital are calculated in the Worksheet.
- All money math uses `Decimal`.

**Not modeled:**
- Multi-line (compound) journal entries.
- Closing entries, post-closing trial balance, reversing entries, or accounting periods.
- Separate printed Income Statement, Statement of Owner's Equity, or Balance Sheet screens (they exist only as Worksheet columns).
- A separate contra-account type (for example, Accumulated Depreciation is stored as an Asset).

## 6. Product Boundaries

- One local JSON file; no user accounts, cloud sync, multi-user editing, audit trail, or database.
- No import of external accounting data; exports are snapshots.
- No Undo/Redo, Preferences, in-app documentation, or printing.
- No in-app restore from backup (restoring is a manual file rename).
- No rename or manual delete of custom accounts (they appear when used and disappear when unused).

## 7. Product Decisions Already Made

- **Click-to-unlock inputs are intentional.** An earlier plan to remove them was cancelled by the user. Do not remove or redesign them without a new request.
- **Menu cleanup is done.** Undo, Redo, Preferences, Documentation, and Recalculate Worksheet were removed as unfinished or redundant. Do not add placeholder actions that do nothing.
- **Kept on purpose:** bulk selection and bulk deletion, the All Accounts ledger, Excel and PDF export, Validate Data, Backup Manager.
- **Delete Entry** works only from the Journal tab; elsewhere it tells the student to use the Journal.
- **Accounting rules are fixed:** one debit account, one credit account, positive amount, different accounts, `Decimal` math. Display tweaks must not change these.

## 8. Known Product Gaps

These affect what students experience today. Items marked **FIXED** were resolved during the merge with the team member's visual redesign branch.

1. **Worksheet CSV export crashes** (recursion). **FIXED 2026-11-17** — now calls `WorksheetMixin.export_csv(self)` directly in `main.py`; **FIXED 2026-11-21** — renamed to `export_worksheet_csv`, eliminating the name collision entirely.
2. **No on-screen balance check** for the Worksheet — **ON HOLD** (deferred per product decision).
3. **No per-row running balance** on the Ledger screen (only totals); the CSV has one — **INTENTIONAL** (follows instructor's T-account format).
4. **Ledger and CSV order follow the order entries were added, not their dates.** A back-dated entry can make a ledger running balance look out of date order. The Journal screen alone sorts by date.
5. **Refresh (F5) while editing an entry discards the edit.** (by design; refresh clears form)
6. **The "Entry added/updated" confirmation message is cleared immediately** by the refresh that follows saving.
7. **Corrupt data file:** the app starts with empty data and shows a warning, but the next save replaces the unreadable file (its old content is kept only as a backup). **PARTIALLY FIXED 2026-11-21** — the unreadable file is now kept as `accounting_data.unreadable.<timestamp>.json` and never auto-deleted; the app still starts with empty data after a failed load.
8. **A bad amount in the data file stops the app from starting.** If `accounting_data.json` contains an entry whose amount is not a number (for example after a hand edit), the app closes at launch with no message, and *Validate Data* cannot be reached. **FIXED 2026-11-20** — `_validate_data` now validates amounts, dates, and account names on load; shows warning with count of skipped entries; app no longer crashes. (found 2026-11-20, tested)
9. **Backups only reach back 5 saves.** Each add, edit or delete makes one backup and only the newest 5 are kept, so older versions are gone after a few minutes of work. Saves in the same second share one backup. A crash while saving can also leave a damaged data file. **FIXED 2026-11-21** — microsecond resolution prevents overwrites; `MAX_BACKUPS=20`; identical consecutive saves skip backup; atomic temp-file save prevents damaged data file on crash. (found 2026-11-20)
10. **Blank descriptions appear as `[wala ni enter ug description]`** in the Ledger and in every export. **FIXED 2026-11-21** — blank descriptions now stored as empty string; Ledger fallback works for new entries; exports show empty cell; old placeholder entries preserved. (found 2026-11-20)
11. **A failed save is easy to miss.** An error dialog appears, but the screen still shows the entry as added, and it exists only in memory until a later save succeeds. **FIXED 2026-11-21** — `save()` now returns True/False; `add_entry` and `delete_multiple_entries` take snapshots before changes and restore on failure, keeping the form/selection and showing no success message. (found 2026-11-20)
12. **Student data and tooling are committed to the repository** (backup JSON files, `.claude/` and `.impeccable/` folders) because `.gitignore` only lists the main data file. (found 2026-11-20)

## 9. Product Principles

1. **Start immediately:** `python main.py` works without installing anything for core use.
2. **Make the accounting cycle visible:** every view is derived from the same journal data.
3. **Protect student work:** validate input, confirm deletion, back up before saving.
4. **Keep accounting rules explicit:** show Dr/Cr columns and totals rather than hiding calculations.
5. **Keep the interface approachable:** clear labels, keyboard access, readable tables, helpful empty states.
6. **Be honest:** never show a control that does nothing, and never claim a feature works that has not been tested.

## 10. Acceptance Checks for Changes

A change is acceptable only if all of these still hold:

- A valid entry appears correctly in the Journal, the Ledger, and the Worksheet.
- Invalid amounts and identical debit/credit accounts are rejected.
- Adjusting entries land in the Adjustments columns and are marked `[Adj]` in the Ledger.
- Worksheet Dr and Cr totals agree for Trial Balance, Adjustments, Adjusted Trial Balance, Income Statement, Owner's Equity, and Balance Sheet.
- A new custom account appears in both dropdowns while used and disappears after its last entry is deleted.
- Saving creates a backup and keeps at most 5.
- A corrupt data file is never replaced silently with empty data without the student being warned.
- Core use works with neither `openpyxl` nor `reportlab` installed.
- Journal CSV, Ledger CSV, and **Worksheet CSV export** work from their respective tabs.
- Excel and PDF export work when their packages are installed.

## 11. How This Document Was Verified

**Done:** compared the previous `PRODUCT.md` with all ten Python files; re-read `ARCHITECTURE.md`, `MEMORY.md`, `SESSION_HANDOFF.md`,
and `FEATURE_SIMPLIFICATION_PLAN.md`; confirmed the worksheet math, custom-account cleanup, backup limit, and Worksheet CSV crash by running
the logic with Tkinter stubbed on synthetic data (the real data file and backups were not used).

**GUI launched and verified post-merge:** application starts successfully; visual layout confirmed (seamless light-gray background across root/notebook/tabs, thin `BORDER_STRONG` separators between sections, compact spacing per updated scale, labels blend into panel background, Worksheet tab title left + exports right, Journal table PRIMARY header with empty state icon, Ledger fixed-height top bar, About dialog two-column layout).

**Not done:** running Excel/PDF export with real data; trying forms, dialogs, selection, or menus by hand.

**Corrections from the previous version:** the running balance is not shown on every Ledger row; Worksheet "balance checks" are computed
but not displayed; Worksheet CSV export was broken (recursion) — **now fixed**.
