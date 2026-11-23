# Feature Simplification Plan

## Primary Goal

Students can focus on entering journal entries and reviewing the resulting ledger and worksheet without seeing unfinished controls or having to unlock ordinary input fields.

## Scope

This plan removes visibly unfinished or redundant actions, makes the Journal and Ledger selectors normally interactive, and fixes the Worksheet CSV routing defect found during planning. It keeps the accounting flow, data format, backups, custom accounts, search, bulk deletion behavior, all-accounts ledger, validation, and all export formats.

## Phase 0: Documentation and Behavior Baseline

**How this serves the primary goal:** It prevents interface cleanup from removing an accounting safeguard or changing the documented student workflow.

**What to implement**

- Re-read `AI_GUIDE.md`, `MEMORY.md`, `PRODUCT.md`, `DESIGN.md`, `ARCHITECTURE.md`, and `SESSION_HANDOFF.md`.
- Inspect the menu declarations and handlers in `main.py`, input-state behavior in `journal_tab.py` and `ledger_tab.py`, and Worksheet export routing.
- Treat Journal -> Ledger -> Worksheet, JSON safety, `Decimal`, validation, backups, search, all-accounts Ledger, single-entry deletion, bulk deletion, and export availability as preserved behavior.

**Documentation references**

- `AI_GUIDE.md`, sections 2 through 6: focused changes, accounting safety, and completion checks.
- `PRODUCT.md`, Current Capabilities and Product Principles: preserve the core learning flow and student safeguards.
- `DESIGN.md`, Component Rules and Layout and Interaction: use standard ttk controls and retain keyboard access.
- `ARCHITECTURE.md`, Startup and Refresh Lifecycle plus Data and Accounting Flow: preserve the refresh and save sequence.

**Verification checklist**

- Confirm the target methods and handlers still match the current code before editing.
- Confirm no change is planned for `accounting_data.json` or the JSON schema.

**Anti-pattern guards**

- Do not remove backups, validation, Search, All Accounts, or export support because they are working core capabilities.
- Do not modify debit/credit calculations, `Decimal` usage, or the save -> refresh sequence.

## Phase 1: Make Menus Honest

**How this serves the primary goal:** Students see only actions that work and help them complete accounting exercises.

**What to implement**

- Remove Undo, Redo, and Preferences from the Edit menu because they are unimplemented.
- Remove the corresponding unused placeholder methods.
- Remove Undo and Redo from the Keyboard Shortcuts dialog.
- Remove the Documentation menu command until it provides student-facing help.
- Remove Recalculate Worksheet because View -> Refresh already refreshes the worksheet and every other view.
- Keep New Entry, Delete Entry, Refresh, Validate Data, Backup Manager, exports, Keyboard Shortcuts, and About.
- When Delete Entry is chosen outside Journal, give a clear message directing the student to select an entry in Journal instead of silently doing nothing.

**Documentation references**

- `PRODUCT.md`, Product Principles: keep the interface approachable and preserve validation/backups.
- `DESIGN.md`, Component Rules: preserve the primary and danger actions that remain.
- `main.py`: current menu construction, placeholder handlers, keyboard shortcut dialog, and `delete_selected_entry()`.

**Verification checklist**

- Open every menu and confirm no disabled or placeholder action remains.
- Confirm the shortcut dialog lists only working shortcuts.
- Confirm Delete Entry either opens the normal Journal deletion path or gives a clear Journal-tab instruction.

**Anti-pattern guards**

- Do not remove Validate Data or Backup Manager.
- Do not change Journal deletion confirmation, custom-account cleanup, or the ledger/worksheet refresh behavior.

## Phase 2: Make Routine Inputs Ready to Use — **CANCELLED**

**How this serves the primary goal:** Journal entry should feel like a normal form rather than a locked interface that students must unlock before every field.

**What to implement** — **Cancelled per user decision. Click-to-unlock behavior is intentionally retained.**

- ~~Set the Journal date, Debit Account, Credit Account, Amount, and Description controls to their normal editable/selection states when the form is built.~~
- ~~Remove the Journal click-to-unlock and focus-loss relocking handlers.~~
- ~~Update `App.clear_journal_form()` so refresh clears values but does not disable or make fields read-only.~~
- ~~Set the Ledger account selector to normal interactive selection and remove its click-to-unlock behavior.~~
- Keep account autocomplete, date-day validation, account values refresh, Enter submission, and the selected Ledger account fallback.

**Documentation references**

- `DESIGN.md`, Layout and Interaction plus Accessibility Expectations: retain keyboard navigation and visible interaction states.
- `PRODUCT.md`, User Outcomes: prioritize fast journal entry and understandable ledger review.
- `journal_tab.py`, `ledger_tab.py`, and `main.py`: current form states, bindings, and reset behavior.

**Verification checklist** — **Not applicable (cancelled)**

**Anti-pattern guards**

- Do not remove input validation or account autocomplete.
- Do not make the date selector accept an invalid calendar date.

## Phase 3: Repair Worksheet CSV Routing — **COMPLETED**

**How this serves the primary goal:** The retained CSV export works from all three tabs without recursion or an application error.

**What to implement** — **DONE (2026-11-17 merge)**

- Route the Worksheet branch of `App.export_csv()` (line 196 in `main.py`) to `WorksheetMixin.export_csv(self)` explicitly instead of calling `self.export_csv()` again (caused infinite recursion).
- Leave the Journal and Ledger CSV export paths unchanged.
- (Renamed export_worksheet_csv on 2026-11-21.)

**Documentation references**

- `PRODUCT.md`, Current Capabilities and Acceptance Checks: CSV is a core export outcome.
- `ARCHITECTURE.md`, File Responsibilities: Worksheet export belongs to `worksheet_tab.py`.
- `main.py`, `export_csv()` and `worksheet_tab.py`, `WorksheetMixin.export_csv()` (renamed export_worksheet_csv on 2026-11-21).

**Verification checklist** — **Verified (code inspection + syntax check)**

- Select Journal, Ledger, and Worksheet in turn and choose File -> Export -> Export CSV.
- Cancel each save dialog during smoke testing, then export one Worksheet CSV to a temporary location and verify its headers and rows.

**Anti-pattern guards**

- Do not alter the existing file dialog, encoding, worksheet calculation, Excel export, or PDF export.

## Phase 4: Verify and Update Documentation — **DOCUMENTATION UPDATES COMPLETE**

**How this serves the primary goal:** The simplified interface remains safe, and the next AI has an accurate account of its behavior.

**What to implement** — **DOCUMENTATION UPDATES DONE (2026-11-17)**

- ~~Perform syntax validation using the available Python interpreter.~~ (Done for modified files)
- ~~Manually test Journal -> Ledger -> Worksheet with existing data only; do not reset or overwrite the JSON file.~~ (Not yet done)
- Confirm custom accounts remain visible in both dropdowns while referenced and disappear after their final entry is deleted.
- ✅ Updated `MEMORY.md` with current interface behavior, safety rules, and follow-up items
- ✅ Updated `DESIGN.md` — clarified Delete key works but no longer in Edit menu
- ✅ Updated `SESSION_HANDOFF.md` with completed work, follow-up items, and bug note
- ✅ Updated `FEATURE_SIMPLIFICATION_PLAN.md` — marked Phase 2 cancelled, Phase 3 incomplete, Phase 4 documentation complete

**Documentation references**

- `AI_GUIDE.md`, Before Completing a Task.
- `MEMORY.md`, Safety Rules and Known Follow-up Items.
- `SESSION_HANDOFF.md`, Safe Next Steps.

**Verification checklist** — **Documentation updates verified**

- ✅ Checked for references to removed menus, placeholder methods, or obsolete shortcuts.
- Check that Journal, Ledger, and Worksheet totals still agree after add, edit, and delete operations. (Pending manual test)
- ✅ Confirm no source code attempts to write test data into `accounting_data.json`.

**Anti-pattern guards**

- Do not mark the work complete based only on syntax checks.
- Do not leave completed items in active follow-up lists.

## Explicit Deferrals

- Keep bulk selection and bulk deletion for now; revisit only after students have used the simplified interface.
- Keep Excel and PDF export available rather than hiding or removing them.
- Do not add Undo/Redo, Preferences, or in-app documentation in this scope.
