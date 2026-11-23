# Project Memory

> **Purpose:** A short, trustworthy briefing for any AI assistant or developer starting work on this project:
> what it is, its current state, the rules that must not be broken, decisions already made, and open items.
> It is a summary. Details live in the files named in §9.
>
> **Authority:** Current source code beats this file. If something here no longer matches the code, verify,
> then correct this file. Do not treat an item as still true just because it is written here.
>
> **Last reviewed:** 2026-11-17, against the source files after the merge with team member's visual redesign. GUI launched and verified.
> **Re-reviewed:** 2026-11-20 (documentation pass). Logic re-tested with Tkinter stubbed; new findings are in §7 items 16-23. No source code was changed.

---

## 1. Purpose

Accounting App is an offline Python/Tkinter desktop application for BSIT 2nd Year, 1st Semester, Group 3.
It teaches the accounting cycle: a student records journal entries, and the app derives a **Ledger** and a **12-column Worksheet** from them.
It is a teaching tool, not a production bookkeeping, tax, or multi-user system.

## 2. Current State

- **Launch:** `python main.py`
- **Runtime:** Python 3.10+ and the standard library only (Tkinter/`ttk`).
- **Optional packages:** `openpyxl` (Excel export), `reportlab` (PDF export). Core use must work without them.
- **Code layout:** one `App` class assembled from mixins; modules are `main.py`, `data.py`, `constants.py`, `style.py`,
  `journal_tab.py`, `journal_table.py`, `ledger_tab.py`, `worksheet_tab.py`, `grid_table.py`, `about_tab.py`. See `ARCHITECTURE.md`.
- **Data file:** `accounting_data.json` beside the code. It is listed in `.gitignore`, so **a fresh copy of the project has no data file** and the app starts empty.
  The ZIP reviewed on 2026-11-20 contains no `accounting_data.json`, only five backup files (5–7 entries each, all valid JSON, all balanced on the Worksheet). **FIXED 2026-11-21:** `.gitignore` now ignores `accounting_data.backup.*.json`, `accounting_data.unreadable.*.json`, `accounting_data.json.tmp`, and `.claude/` — future backups and assistant tooling will not be committed. Files already committed need `git rm --cached` by the human.
- **Backups:** `accounting_data.backup.YYYY-MM-DD_HH-MM-SS.json`, created before each save. The app deletes older ones so at most **20** remain
  after a save (updated from 5 on 2026-11-21). Treat all backups as user data.
- **Documentation set:** `AI_GUIDE.md`, `DESIGN.md`, `ARCHITECTURE.md`, `PRODUCT.md`, `MEMORY.md`, `SESSION_HANDOFF.md` all updated to reflect merged state.
- **Recent merge:** Merged team member's visual redesign (beamerge branch) with this branch's bug fixes. Result: blue design system preserved, team's UX improvements adopted (canvas checkbox, search placeholder, custom dialogs, thin separators, Worksheet title+right-aligned exports), critical bugs fixed (Worksheet CSV recursion, corrupt JSON f-string, right-click menu), spacing compacted to middle ground.

## 3. Accounting Model

Each journal entry is one balanced debit/credit pair:

```json
{
  "date": "YYYY-MM-DD",
  "debit": "Account name",
  "credit": "Account name",
  "amount": "100.00",
  "desc": "Explanation",
  "adj": false
}
```

- `amount` is a string on disk, converted to `Decimal` for every calculation. Never use floats for money.
- The form requires a valid date, two different accounts, and a positive amount (stored with 2 decimals).
- A blank description is saved as an empty string `""` (previously `[wala ni enter ug description]`, fixed 2026-11-21). Old entries that already contain the placeholder text are left unchanged and must not be rewritten without a request.
- `adj: true` sends an entry to the Worksheet **Adjustments** columns; otherwise it goes to **Trial Balance**.
- Account type decides the statement column: Asset/Liability → Balance Sheet; Owner's Capital/Drawings → Owner's Equity; Revenue/Expense → Income Statement.
- The chart has 27 predefined accounts. A typed new name prompts for a type and is stored in `custom`.
  A custom account exists only while an entry uses it; it is removed when its last entry is deleted. Account names found only in entries (legacy data) are treated as **Asset**.
- Ledger and Worksheet are always recomputed from `entries`. Nothing derived is saved.
- `entries` keeps insertion order. Only the Journal screen sorts by date; the Ledger and CSV exports follow insertion order.

## 4. Application Flow

1. `main.App` loads `entries` and `custom` through `DataMixin`.
2. `JournalMixin` validates, adds, edits, or deletes entries, then runs: **update `entries` → `sync_custom_accounts()` → `save()` → `App.refresh()`**. Keep this order.
3. `App.refresh()` rebuilds dropdowns, clears the ledger cache, refreshes Journal, Ledger and Worksheet, and clears and locks the Journal form
   (so F5 also discards an edit in progress).
4. `LedgerMixin` and `WorksheetMixin` derive their displays from `entries`. `_compute_account_ledger` lives in `main.py`.

## 5. Safety Rules

- Preserve `Decimal` calculations.
- Do not change debit/credit rules, account classification, worksheet formulas, backup behavior, or JSON-recovery behavior without focused verification.
- Never overwrite, reset, or use the real `accounting_data.json` (or its backups) for tests. Use a copy or a temporary dataset.
- Do not replace unreadable data with an empty dataset automatically.
- **Click-to-unlock inputs are intentional.** Do not remove or redesign them unless the user asks.
- Do not add controls that look functional but do nothing.
- **Method-name trap:** `App` and the mixins share one namespace, and the first definition wins silently
  (`App` → `DataMixin` → `StyleMixin` → `JournalMixin` → `LedgerMixin` → `WorksheetMixin`). Search all files before adding or renaming a method.
- Before working on a task, read `AI_GUIDE.md` and the documents relevant to it.

## 6. Decisions Already Made

- Click-to-unlock behavior for Journal and Ledger inputs is **kept**. The plan to make inputs always editable was cancelled by the user.
- Menu cleanup is **done**: Undo, Redo, Preferences, Documentation, and Recalculate Worksheet were removed. Delete Entry outside the Journal shows a message.
- Bulk selection/deletion, the All Accounts Ledger, Excel and PDF export, Validate Data, and Backup Manager are kept on purpose.
- Custom accounts are saved with the type the student chooses; legacy untyped custom accounts are restored as Assets.
- The duplicate `_compute_account_ledger` in `ledger_tab.py` was removed; the `main.py` version is the one in use.
- **Design system**: Blue palette (`#2563EB` primary) preserved from this branch; team's warm beige palette not adopted.
- **Spacing**: Compact middle ground between this branch (generous) and team branch (tight) — `SPACE_2=6`, `SPACE_3=10`, `SPACE_4=14`, `SPACE_5=16`, `SPACE_6=18`, `SPACE_8=24`; table row height 28px, header 32px.
- **Visual polish adopted from team**: Canvas-drawn Adjusting Entry checkbox, search placeholder with focus handling, canvas-rendered status badges, custom modal dialogs, thin `BORDER_STRONG` separators between sections, Worksheet tab with left title + right-aligned exports, About dialog two-column layout, Ledger fixed-height top bar with custom combobox style, Journal table PRIMARY header with empty state icon.

## 7. Known Follow-up Items

Verified during the 2026-11-17 review and post-merge testing. **Documented only; no code was changed.** Full details and evidence are in `ARCHITECTURE.md` §13.

**Needs a decision or fix**

1. **Worksheet CSV export crashes** (infinite recursion). In `App.export_csv` (`main.py`), the Worksheet branch calls `self.export_csv()`, which is `App.export_csv` itself.
   The intended target is `WorksheetMixin.export_csv(self)`, which is shadowed. The Worksheet tab's Export CSV button hits the same path. **FIXED 2026-11-17** — now calls `WorksheetMixin.export_csv(self)` directly; **FIXED 2026-11-21** — renamed to `export_worksheet_csv`, eliminating the name collision entirely.
2. **Corrupt data file handling:** after a failed load the app holds empty data, and the next save overwrites the unreadable file
   (its content survives only as the newest backup, which can push older good backups out of the 5-file limit). **PARTIALLY FIXED 2026-11-21** — the unreadable file is now preserved as `accounting_data.unreadable.<timestamp>.json` and never auto-deleted; the app still starts with empty data after a failed load.
3. **Corrupt-file dialog text bug:** in `data.py` the string containing `{backup_msg}` lacked an `f` prefix. **FIXED in merge** — now interpolates correctly.
4. The "Invalid Data Format" dialog says valid entries will be kept, but the app starts with empty data.
5. **Right-click menu on Journal rows:** `_create_context_menu` is never called, so the menu would fail. **FIXED in merge** — now called in `build_journal()`.

**Product gaps and smaller observations**

6. No on-screen Worksheet balance indicator (the checks are computed and discarded) — **ON HOLD** (deferred per product decision).
7. The Ledger screen shows no per-row running balance; only totals. The CSV has it — **INTENTIONAL** (follows instructor's T-account format).
8. Success message after add/update is cleared immediately by refresh (code reading only).
9. `clear_journal_form` **FIXED** — now resets `v_month`, `v_day`, `v_year` to today. Previously referenced non-existent `v_date`.
10. If the credit account's type dialog is cancelled after the debit account was added as custom, that custom account lingers until the next sync — **FIXED** (resolve() no longer mutates self.custom; both accounts added atomically).
11. (Previously listed dead code items were incorrect or already resolved. `JournalMixin.refresh` was removed in merge 3cca37d; `fmt_amt` defined once in `style.py`; `fmt_tree`, `constants.FONT`, `constants.date_to_iso` never existed; `preserve_selection` is actively used.)

**New findings from the 2026-11-20 review** (documented only; details and evidence in `ARCHITECTURE.md` §13, numbers in brackets)

16. **[#16, High] A bad `amount` in the data file crashes the app at launch.** The load validator keeps entries with a non-numeric amount; the first refresh then raises `InvalidOperation` and the app closes with no dialog. **FIXED 2026-11-20** — `_validate_data` now validates amount (Decimal, finite, >0), date format, non-empty debit/credit strings, coerces `adj` to bool, normalizes amount to 2-decimal string. Shows warning dialog with count of skipped entries. *Tested.*
17. **[#15, High] The data file is written in place, not atomically.** A crash mid-write can truncate it (the corrupt-file case in item 2). **FIXED 2026-11-21** — `save()` now builds JSON text first, writes to `DATA_FILE.tmp`, calls `flush()` + `os.fsync()`, then `os.replace()` for atomic swap. Temp file cleaned up on any error. Existing error dialogs unchanged. *Tested.*
18. **[#17, Medium] Backups only cover the last 5 saves,** names have 1-second resolution (9 rapid saves left 1 backup), and after a failed load plus save the newest backup is the unreadable file. **FIXED 2026-11-21** — microsecond resolution prevents overwrites; `MAX_BACKUPS=20`; identical consecutive saves skip backup; unreadable file preserved as `accounting_data.unreadable.<timestamp>.json` and never cleaned up. **Note:** backups now contain the NEW data as saved, not the previous file — the newest backup equals the current data file; to go back one step use the second newest. *Tested.*
19. **[#18, Medium] Student data is committed:** `.gitignore` ignores only `accounting_data.json`, so the `accounting_data.backup.*.json` files are in the repo. The `.claude/skills/impeccable/` folder (with a Windows `.exe`) and `.impeccable/` are committed too. **FIXED 2026-11-21** — .gitignore now ignores accounting_data.backup.*.json, accounting_data.unreadable.*.json, accounting_data.json.tmp, and .claude/. .impeccable/ intentionally stays tracked (DESIGN.md references .impeccable/surfaces/ledger-tab.md). Files already committed need `git rm --cached` by the human.
20. **[#19, Medium] The default description `[wala ni enter ug description]` shows up in the Ledger and every export,** and it blocks the Ledger's "other account" fallback for form entries. **FIXED 2026-11-21** — blank descriptions now stored as empty string `""`; Ledger fallback works for new entries; CSV/Excel/PDF exports show empty cell; old entries with placeholder preserved unchanged. *Tested.*
21. **[#20, Low] A failed `save()` is invisible to its callers:** it shows a dialog and returns `None`, and the UI still shows the change as saved. **FIXED 2026-11-21** — `save()` now returns True on success, False on failure. `add_entry` and `delete_multiple_entries` take deepcopy snapshots before changes; on save failure they restore the snapshots, refresh, keep the form/selection as-is, and do not show a success message. *Tested.*
22. **[#21, Low] A data file that is not valid UTF-8 is reported as "Invalid Data Format"** (`UnicodeDecodeError` is a `ValueError`).
23. **[§12.1, Low] The `export_csv` name is still defined twice.** **FIXED 2026-11-21** — Renamed `WorksheetMixin.export_csv` to `export_worksheet_csv` (definition and button command in `worksheet_tab.py`); dispatcher in `main.py` calls `self.export_worksheet_csv()`. `_compute_account_ledger` duplicate removed from `main.py`, kept in `ledger_tab.py`. Name collision eliminated. *Tested.*

**Manual testing still needed** (nothing below has been run in the real GUI)

12. Add, edit, delete, search, bulk delete, and F5 in the Journal; click-to-unlock behavior.
13. A new custom account appears in Journal and Ledger dropdowns, and disappears after its final entry is deleted.
14. Journal, Ledger, and Worksheet totals agree after add, edit, and delete.
15. Excel and PDF export, with and without the optional packages installed.

Behavior note: loading skips individual entries that are missing required fields without any warning; a malformed top-level file triggers a dialog.

## 8. Verification Status

- Source read: all ten Python files, completely. Syntax check (`py_compile`): passed.
- Run with Tkinter stubbed on synthetic data: method resolution, the CSV recursion, worksheet math (profit, loss, drawings, adjustments, legacy accounts),
  custom-account cleanup, ledger ordering, and every load/save/backup path.
- GUI launched successfully post-merge; visual layout verified (seamless background, thin separators, compact spacing, label blending, Worksheet tab layout).
- Excel/PDF exports not run; interactive behavior (click-to-unlock, dialogs, right-click) not manually tested.
- 2026-11-20: all `.py` files compile; with Tkinter stubbed (Tkinter was not installed, so the GUI was not launched) on a copy of the code: Worksheet balances on all five backup datasets; non-numeric amount crashes Worksheet and Ledger math; blank-description placeholder reaches Ledger particulars; truncated-file load plus save; backup rotation; failed save returns `None`; Worksheet CSV dispatch has no recursion.

## 9. Where to Look

| Need | File |
|---|---|
| Working rules, change workflow, completion report format | `AI_GUIDE.md` |
| Module map, data flow, worksheet algorithm, known issues in detail | `ARCHITECTURE.md` |
| What the product does and does not do | `PRODUCT.md` |
| Colors, spacing, components, interaction rules | `DESIGN.md` |
| Latest handoff notes | `SESSION_HANDOFF.md` |
| Earlier simplification plan (Phase 2 cancelled, Phase 3 not done) | `FEATURE_SIMPLIFICATION_PLAN.md` |
| Ledger screen design brief | `.impeccable/surfaces/ledger-tab.md` |