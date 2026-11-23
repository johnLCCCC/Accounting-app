# AI Guide — Accounting Application

This guide defines how an AI assistant should inspect, modify, verify, and explain work on this project. Follow it before making code or documentation changes.

## 1. Project at a Glance

The Accounting App is an offline Python desktop learning application built with Tkinter and `ttk`.

- **Primary users:** BSIT 2nd Year, 1st Semester students learning the accounting cycle.
- **Main workflow:** record a journal entry, then review its derived Ledger and 12-column Worksheet results.
- **Application entry point:** `main.py`
- **Core runtime:** Python 3.10+ and the Python standard library, including Tkinter.
- **Persistent data:** `accounting_data.json`, stored beside the application files.
- **Optional export dependencies:** `openpyxl` for Excel and `reportlab` for PDF.
- **Connectivity:** no internet connection or remote service is required.

This is a teaching application, not a production bookkeeping, tax, or multi-user accounting system.

## 2. Required Project Reading

Before substantive work, read the project documents that are relevant to the task:

1. `MEMORY.md` — current project state, data model, safety rules, and known follow-up items.
2. `PRODUCT.md` — intended users, workflows, capabilities, and product boundaries.
3. `DESIGN.md` — implemented visual tokens and interface standards.
4. `ARCHITECTURE.md` — module responsibilities, dependencies, and data flow.
5. `SESSION_HANDOFF.md` — latest handoff notes, recent changes, verification status, and known issues.

Then inspect the actual source files involved. Documentation is context, not a substitute for reading the implementation.

### When information conflicts

Use this order to resolve conflicts:

1. The user's latest explicit requirement determines the requested outcome.
2. The current source code determines what is actually implemented.
3. Current project documentation describes intended behavior and recorded decisions.
4. Do not silently resolve a conflict by guessing. Explain it and ask if it affects the requested change.

Do not assume that a note in a handoff file is still current without checking the relevant code.

## 3. General Working Principles

1. **Make focused changes.** Modify only the files needed for the requested task.
2. **Understand before editing.** Trace relevant functions, callbacks, imports, and shared state before changing behavior.
3. **Preserve existing features.** Do not remove, hide, or replace functionality without permission.
4. **Preserve the architecture.** Reuse the existing modules, mixins, helpers, and conventions where practical.
5. **Keep implementations simple.** Avoid unnecessary dependencies, abstractions, duplicated functions, and speculative refactors.
6. **Do not invent behavior.** If the current implementation or requirements are unclear, inspect further or ask.
7. **Separate UI work from logic work.** A visual change must not accidentally alter accounting calculations, persistence, validation, or event behavior.
8. **Report verification honestly.** Distinguish checks actually performed from checks the user still needs to perform.

## 4. Architecture and Data Ownership

The application is a single-process Tkinter program. `main.py` defines the `App` class and composes focused mixins.

| Module | Responsibility |
|---|---|
| `main.py` | Application shell, menus, shared state and refresh, and Journal/Ledger CSV export |
| `constants.py` | Chart of accounts, account categories, shared numeric/date constants, and formatting helpers |
| `data.py` | JSON validation, loading, saving, backup retention, and account-name/type helpers |
| `style.py` | Theme tokens, ttk styling, shared Treeview construction, and table tags |
| `journal_tab.py` | Journal form, validation, account resolution, search, edit, and delete workflows |
| `journal_table.py` | Journal table rendering, selection, and row callbacks |
| `ledger_tab.py` | Account selection and derived Ledger display |
| `worksheet_tab.py` | Worksheet calculations, rendering coordination, and worksheet exports |
| `grid_table.py` | Canvas-based worksheet grid and grouped headers |
| `about_tab.py` | About dialog |

### Data ownership rules

- `App.entries` is the in-memory collection of journal entries.
- `App.custom` stores custom account names and their account types.
- `accounting_data.json` is the persisted source for journal data and custom account data.
- The Ledger and Worksheet are derived views. Do not introduce separate persisted copies of their balances.
- `constants.CHART` supplies the predefined chart of accounts and account categories.
- The shared refresh flow invalidates the Ledger cache and refreshes the affected views after saved journal changes.

Before changing a data field or its meaning, trace every reader and writer, including JSON validation, save/load code, Journal, Ledger, Worksheet, and exports.

## 5. Accounting and Calculation Rules

These rules are critical. Do not change them as part of an unrelated UI or cleanup task.

- Every current journal entry represents one debit account, one credit account, and one amount.
- Debit and credit accounts must be different.
- The amount must be positive.
- Monetary calculations must use `Decimal`, not binary floating-point arithmetic.
- Amounts are stored as strings in JSON and converted to `Decimal` for calculations.
- Journal entries must remain balanced.
- Ledger activity and balances must be derived from the journal entries.
- Worksheet totals and balance checks must remain consistent with the same journal data.
- Entries marked `adj: true` belong in the Worksheet Adjustment columns; regular entries belong in the Trial Balance columns.
- Account classification must continue to respect the predefined chart, stored custom account types, and the documented legacy-account fallback behavior.

Never alter debit/credit rules, account classification, adjustment handling, statement destinations, or worksheet formulas merely to make a displayed total look correct.

For an accounting-related change, trace the calculation from Journal data through Ledger and all affected Worksheet columns. Verify both individual account results and totals.

## 6. Data Safety and Recovery

Treat the existing `accounting_data.json` and its backups as user data, even if the file currently contains sample records.

- Never delete, reset, replace, or overwrite existing accounting records without explicit permission.
- Do not use the real project data file as a test fixture.
- If testing requires data changes, use a separate copied project/data file or an isolated temporary test dataset.
- Preserve the automatic backup behavior and backup retention policy.
- Do not replace a missing, malformed, or unreadable data file with an empty dataset automatically.
- Preserve the current recovery guidance when JSON loading fails.
- Do not expose real accounting records in logs, screenshots, test output, or examples unnecessarily.

If a task touches persistence, inspect `data.py` and the load/save call sites before editing. Confirm that a failed load cannot silently destroy or replace the original data.

## 7. Interface and Design Rules

For UI changes, follow `DESIGN.md` and inspect `style.py` before introducing new styling.

- Use the existing shared color, typography, spacing, and table tokens.
- Prefer updating shared styles in `style.py` over adding inconsistent one-off widget styling.
- Keep the interface calm, readable, and suitable for data-dense accounting tables.
- Preserve the established table alignment: descriptive/date fields are left-aligned and numeric amount fields are right-aligned.
- Keep table dimensions and component behavior consistent with the documented design system.
- Preserve visible focus and keyboard accessibility.
- Preserve the intentional click-to-unlock behavior for Journal and Ledger inputs. Do not remove or redesign this behavior unless the user explicitly requests it.
- Do not introduce browser, CSS, or web-framework assumptions. This is a native Tkinter/ttk desktop application.

After changing a shared style, inspect all affected tabs. A change to `style.py` can affect Journal, Ledger, and Worksheet at once.

## 8. Interaction and Feature Preservation

- Preserve existing keyboard shortcuts and their current scope.
- Preserve confirmation steps for destructive actions.
- Keep validation and user-facing error messages clear.
- Preserve the existing save-then-refresh sequence for journal changes.
- Do not move an action to another tab or menu without permission.
- Do not remove a feature because it appears unused; first check references, callbacks, and user requirements.
- Do not add placeholder buttons or menu actions that appear functional but do nothing.

If an interaction changes, trace both its visible control and the callback or command it invokes.

## 9. Known Issue to Check Before Export Work

**Status: FIXED (2026-11-17 merge, renamed 2026-11-21)** — The Worksheet CSV export recursion issue has been resolved. The Worksheet export path in `main.py` now calls `self.export_worksheet_csv()` (renamed from `WorksheetMixin.export_csv`) directly instead of `self.export_csv()`.

Before working on exports:

1. Inspect the current `main.py` and `worksheet_tab.py`; confirm the fix is in place (`export_worksheet_csv` called at line 197 in `main.py`, defined in `worksheet_tab.py`).
2. Test the Worksheet CSV export with a copied dataset.
3. Also check that Journal and Ledger CSV exports still use their intended handlers.

Do not claim this issue is fixed unless the code has been changed and the relevant export path has been tested.

**Re-verified 2026-11-21 [Tested, Tkinter stubbed]:** with the Worksheet tab active, `App.export_csv` calls `self.export_worksheet_csv()` without recursion. The Worksheet tab's button also calls `self.export_worksheet_csv()` directly. The name collision is eliminated.

### Before changing load, save or backups

Read `ARCHITECTURE.md` §10 and §13 #5 and #15-#18 first. The data file is now written atomically via temp file + `os.replace`, the load validator checks amounts/dates/accounts, and up to 20 backups are kept with microsecond-resolution names (no overwrites in same second, duplicate saves skipped, unreadable files preserved). **Each backup is a copy of the NEW data as saved, not the previous file — the newest backup equals the current data file; to go back one step use the second newest.** **`DataMixin.save()` returns True on success, False on failure; callers (`add_entry`, `delete_multiple_entries`) must check the result and undo in-memory changes on failure.** Test any change with a copy of the data, and test the truncated-file, non-numeric-amount and rapid-save cases.

## 10. Change Workflow

Follow this sequence for each task.

### Before editing

1. Restate the requested outcome in concrete terms.
2. Read the relevant project documents.
3. Inspect the relevant implementation and its dependencies.
4. Identify the smallest set of files that need to change.
5. Identify risks to accounting logic, data, shared UI, and existing workflows.
6. Ask a focused question if a requirement or important behavior is ambiguous.

### While editing

1. Make one coherent, focused change at a time.
2. Preserve public method names and callback contracts unless the task requires changing them.
3. Reuse existing helpers and tokens.
4. Avoid unrelated formatting changes and broad rewrites.
5. Do not modify real accounting data.
6. Keep documentation aligned with behavior only when the task includes or requires documentation updates.

### Before reporting completion

1. Run a Python syntax check on the modified Python files.
2. Run relevant automated checks if the project provides them.
3. Test the affected workflow using isolated or copied data when possible.
4. Check nearby workflows that could be affected by shared code.
5. For UI changes, launch the app and inspect the actual rendered result when the environment permits.
6. If the GUI cannot be launched, say so clearly and provide manual test steps.
7. Do not describe an unperformed test as passed.

## 11. Verification Checklist

Use only the checks relevant to the task, but do not skip a check that protects affected behavior.

### Core application

- [ ] Application starts with `python main.py`.
- [ ] No new import or syntax errors are introduced.
- [ ] Core functionality does not depend on optional export packages.

### Journal

- [ ] Valid entries can be added.
- [ ] Invalid amounts and matching debit/credit accounts are rejected.
- [ ] Search, edit, selection, and confirmed deletion still work.
- [ ] Saving an entry refreshes the derived views.
- [ ] Click-to-unlock behavior remains intact.

### Ledger and Worksheet

- [ ] Ledger activity matches the journal entries; running balance shown on Subtotal/TOTALS rows (T-account format).
- [ ] Worksheet regular and adjusting entries appear in the correct columns.
- [ ] Debit/credit totals and balance checks remain correct.
- [ ] Custom account types remain consistent across Journal, Ledger, and Worksheet.

### Persistence and exports

- [ ] Saving preserves existing records and creates the expected backup.
- [ ] A corrupt JSON file is not silently replaced with an empty file.
- [ ] Journal, Ledger, and Worksheet exports use the correct data and handlers.
- [ ] Optional Excel/PDF exports fail gracefully when their packages are not installed.

## 12. Completion Report Format

When delivering a change, include:

1. **What changed** — concise description of the result.
2. **Files modified** — list each file and its purpose in the change.
3. **Why** — explain the reason for the implementation.
4. **Verification** — list checks actually performed and their outcomes.
5. **Manual testing** — state any checks the user still needs to perform.
6. **Risks or limitations** — mention relevant side effects, unresolved issues, or assumptions.

Keep the explanation direct. Do not claim the whole application was tested when only a small part was checked.

## 13. Final Reminder

Improve the existing Accounting App; do not rebuild it without a clear request.

Prioritize, in this order:

1. Accounting correctness
2. User-data safety
3. Stability and preservation of existing workflows
4. Maintainable implementation
5. Clear and consistent interface

When a requested visual improvement conflicts with accounting behavior or data safety, preserve correctness and safety, then explain the trade-off.
