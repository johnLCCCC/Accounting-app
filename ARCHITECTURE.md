# Architecture

> **Purpose:** This document explains how the Accounting App is actually built: which module owns what,
> how data moves, how the accounting numbers are produced, and which parts of the code are fragile.
> It is written for AI assistants and developers who must change the app without breaking it.
>
> **Authority:** The source code is the final authority. This document was written from a full read of
> every `.py` file in the project. If it disagrees with the code, trust the code, then correct this file.
> Read `AI_GUIDE.md` for working rules and `DESIGN.md` for visual rules; this file covers structure and behavior.
>
> **Last updated:** 2026-11-21 (documentation cleanup). Source code WAS changed on 2026-11-20/21 (fixes #16, #15, #17, #19, #1/duplicate methods).
> §13 now lists eight additional findings (#15-#22), and several statements that had gone stale after the 2026-11-17 merge were corrected (§3, §9.2, §10, §12, §13 #2).
>
> **Verification labels** used below:
> **[Tested]** = reproduced by running the code (Tkinter replaced by a stub, synthetic data, never the real data file).
> **[Read]** = established by reading the code only; the GUI was not launched.

---

## 1. System at a Glance

- Single-process, offline desktop app. Python standard library + Tkinter/`ttk`. Entry point: `python main.py`.
- One class, `App` (in `main.py`), is built from five mixins. **All mixins share one `self`**, so any
  method or attribute can be reached from any mixin file.
- One persisted file: `accounting_data.json` (beside the code; listed in `.gitignore`).
- The **Journal is the only source of accounting data**. Ledger and Worksheet are recomputed from it on every refresh;
  nothing derived is saved.
- Optional packages: `openpyxl` (Excel export), `reportlab` (PDF export). Imported only when the export runs.

```text
                         accounting_data.json
                                ^   |
                      save()    |   |  load()
                                |   v
 Journal form ──> JournalMixin ──> App.entries / App.custom  (in-memory source of truth)
                                         |
                              App.refresh()   (after every saved change)
                 ┌───────────────────────┼────────────────────────┐
                 v                       v                        v
         refresh_journal()        refresh_ledger()        refresh_worksheet()
         -> JournalTable          -> Treeview (lt)        -> compute_worksheet()
                                  uses ledger_cache          -> GridTable (wt) + App.ws_rows
```

---

## 2. Module Map

| File | Defines | Responsibility | Project imports |
|---|---|---|---|
| `main.py` | `class App(DataMixin, StyleMixin, JournalMixin, LedgerMixin, WorksheetMixin)` | Window, menu bar, notebook, **`refresh()`**, `clear_journal_form()`, Journal/Ledger CSV export, `export_csv` dispatcher, Validate Data, Backup Manager, Shortcuts dialog | all modules below |
| `constants.py` | constants, `fmt`, `balfmt`, `date_to_display`, `date_to_iso` | Account types, `CHART`, statement routing tables, `HEADS`, `DATA_FILE`, number/date formatting | none |
| `data.py` | `DataMixin`, `MAX_BACKUPS = 20` | `load`, `save`, `_validate_data`, backups, account-name and account-type helpers, custom-account sync | `constants` |
| `style.py` | tokens, `fmt_amt`, `StyleMixin` | Design tokens, `set_style()` (ttk theme), `make_tree()` (styled Treeview), tree row tags | `constants` (lazy, inside functions) |
| `journal_tab.py` | `JournalMixin` | Journal form, validation, account resolution, add/edit/delete, search, selection toolbar, feeding rows to `JournalTable` | `constants`, `style`, `journal_table` |
| `journal_table.py` | `JournalTable(ttk.Frame)` | Canvas-drawn 3-line-per-entry table, single/multi selection, double-click/right-click/Delete/Ctrl+A callbacks | `style` |
| `ledger_tab.py` | `LedgerMixin` | Account selector, Ledger Treeview rendering (uses `ledger_cache`), **`_compute_account_ledger()`** | `constants`, `style` |
| `worksheet_tab.py` | `WorksheetMixin`, `GROUP_TITLES` | `compute_worksheet()` (12-column math), `refresh_worksheet()`, Worksheet CSV/Excel/PDF export | `constants`, `grid_table`, `style` |
| `grid_table.py` | `GridTable(ttk.Frame)` | Canvas-drawn grid with grouped Dr/Cr headers. **Draws only; does no accounting math.** | `style` |
| `about_tab.py` | `show_about(root)` | Modal About dialog (a plain function, not a mixin) | `style` |

There are no circular imports. `constants.py` imports nothing from the project; `style.py` imports `constants` only inside functions.

Non-code files that matter to AI workflows: `AI_GUIDE.md`, `DESIGN.md`, `MEMORY.md`, `PRODUCT.md`, `SESSION_HANDOFF.md`,
`.impeccable/surfaces/ledger-tab.md` (design brief), `.claude/` and `my-skill/` (assistant tooling, unrelated to runtime).

---

## 3. How the Mixins Combine (and a trap)

`App` inherits in this order, which is also the method-lookup order (MRO):

`App` → `DataMixin` → `StyleMixin` → `JournalMixin` → `LedgerMixin` → `WorksheetMixin`

The first class that defines a method name wins, **silently**. **As of 2026-11-21, no duplicate method names remain.**

Previously (pre-2026-11-21):
| Method | Winner (what runs) | Shadowed copy (never runs through `self`) |
|---|---|---|
| `export_csv` | `App.export_csv` in `main.py` | `WorksheetMixin.export_csv` in `worksheet_tab.py` (reachable only through the explicit class call `WorksheetMixin.export_csv(self)` in `main.py`; see §12.1) |
| `_compute_account_ledger` | `App._compute_account_ledger` in `main.py` | `LedgerMixin._compute_account_ledger` in `ledger_tab.py` (identical code) |

**Fixed 2026-11-21 (Task 5):**
- `_compute_account_ledger` removed from `main.py`; `LedgerMixin` version in `ledger_tab.py` is now the single source.
- `WorksheetMixin.export_csv` renamed to `export_worksheet_csv` in `worksheet_tab.py` (definition and button command).
- `App.export_csv` dispatcher now calls `self.export_worksheet_csv()`.
- The Worksheet tab's own **Export CSV** button (`command=self.export_worksheet_csv`) calls `export_worksheet_csv` directly — it does **not** go through the dispatcher any more.

**Rule:** before adding or renaming any method in a mixin, search every `.py` file for the same name.
A new method in a mixin can be silently overridden by `App` or by an earlier mixin.

`App.refresh()` and `clear_journal_form()` touch widgets that are created by the mixins' `build_*` methods, and they guard
each access with `hasattr(self, ...)`. Keep that guard when adding new widget access in `main.py`.

---

## 4. Shared State on `App`

| Attribute | Created in | Meaning | Written by | Read by |
|---|---|---|---|---|
| `root`, `nb` | `App.__init__` | Tk root; the 3-tab `ttk.Notebook` (index 0 Journal, 1 Ledger, 2 Worksheet) | init | menu actions, export dispatch |
| `entries` | `App.__init__`, `load()` | `list[dict]` of journal entries (the source of truth). **List position is an entry's identity.** | `load`, `add_entry`, `delete_multiple_entries` | everything |
| `custom` | `App.__init__`, `load()` | `dict[name -> account type]` for user-created accounts | `load`, `add_custom_account`, `sync_custom_accounts` | `all_account_names`, `types`, `save` |
| `ledger_cache` | `App.__init__` | `dict[account -> (lines, balance, sum_dr, sum_cr)]` | `LedgerMixin` render + Ledger CSV (fill); `App.refresh` (clear) | Ledger render, Ledger CSV |
| `ws_rows` | `App.__init__` | Last computed worksheet rows `(label, 12 cells of Decimal/None, tag)` | `refresh_worksheet` | Worksheet CSV/Excel/PDF export |
| Journal widgets/vars | `build_journal` | `v_dr v_cr v_amt v_desc v_adj v_month v_day v_year v_search`, `cb_month cb_day cb_year cb_dr cb_cr e_amt e_desc`, `add_btn delete_btn cancel_btn`, `status_var status_lbl`, `search_entry search_info`, `selection_toolbar selection_count_var`, `jt` | Journal code, `clear_journal_form` | Journal code, `App.refresh` |
| `_editing_index` | first set in `edit_entry` / `cancel_edit` / `add_entry` | Index into `entries` of the entry being edited, else `None` | Journal code, `clear_journal_form` | `add_entry` |
| Ledger widgets | `build_ledger` | `v_ledger_acct`, `cb_ledger_acct`, `lt` (Treeview) | Ledger code, `App.refresh` | Ledger render, Ledger CSV |
| `wt` | `build_worksheet` | The `GridTable` | `refresh_worksheet` | — |

---

## 5. Data Model

### 5.1 Journal entry (stored in `entries` and in the JSON file)

```json
{ "date": "2026-11-04", "debit": "Cash", "credit": "Owner's Capital",
  "amount": "1000.00", "desc": "Initial investment", "adj": false }
```

- One entry = **one debit account, one credit account, one amount** (no multi-line entries).
- `date` is stored as ISO `YYYY-MM-DD`; screens and CSV show `Mon DD, YYYY` via `date_to_display()`.
- `amount` is a **string** with two decimals (the form calls `Decimal.quantize(Decimal("0.01"))`), converted to `Decimal` wherever math happens.
- `adj: true` routes the entry to the Worksheet *Adjustments* columns; `false` routes it to *Trial Balance*.
- When the form's description is blank, `add_entry` stores an empty string `""` (previously it stored the literal `"[wala ni enter ug description]"`, fixed 2026-11-21). Old entries that already contain the placeholder text are left unchanged.
- `_validate_data` (on load) keeps only entries that have `date`, `debit`, `credit`, `amount` and fills in missing `desc=""` / `adj=False`.
  It validates date format (YYYY-MM-DD), non-empty debit/credit strings, and amount that is a finite Decimal greater than 0.
  Amount is normalized to a 2-decimal string. `adj` is coerced to bool. Everything else is dropped silently **[Tested]**.
  A warning dialog ("Data Load Warning") shows the number of skipped entries; the file on disk is not changed by loading.

### 5.2 File layout

```json
{ "entries": [ ...entries... ], "custom": { "Custom Account": "Expense" } }
```

`DATA_FILE` is built in `constants.py` from the folder of `constants.py`. Backups sit next to it:
`accounting_data.backup.YYYY-MM-DD_HH-MM-SS.json`.

### 5.3 Ordering

- `entries` is kept in **insertion order**. Editing replaces the entry in place.
- The **Journal screen** sorts by `(date, original index)` for display only.
- The **Ledger, Ledger CSV and Journal CSV** use **insertion order**, not date order, so a Ledger running balance follows the order entries were added **[Tested]**.
- The Worksheet is order-independent (it only sums).

---

## 6. Account Names and Types

Three related helpers in `data.py`; choose the right one:

| Helper | Returns | Used for |
|---|---|---|
| `all_account_names()` | `CHART` names + `custom` keys | Journal dropdowns, Ledger dropdown |
| `get_all_account_names()` | the above + any account names that appear only in entries | Worksheet rows, Ledger "All Accounts" |
| `types()` | `{name: type}` from `CHART`, then `custom`; unknown entry-referenced names default to **Asset** | Worksheet classification |

`constants.py` supplies `CHART` (27 predefined accounts with a type), the six types
(`Asset, Liability, Owner's Capital, Owner's Drawings, Revenue, Expense`), and two routing tables:

```text
SECTION     = Asset/Liability -> "BS";  Owner's Capital/Drawings -> "OE";  Revenue/Expense -> "IS"
SECTION_COL = "IS" -> column 6,  "OE" -> column 8,  "BS" -> column 10   (index of that statement's Dr column)
```

**Custom accounts.** Typing an unknown name in a Journal account box triggers `resolve()` → `ask_type()` (a modal type picker) →
`add_custom_account()`. Matching of typed text to existing names is case-insensitive.
`sync_custom_accounts()` (run on load, after add/edit, after delete) then:
1. adds any entry-referenced non-chart name missing from `custom` as **Asset** (legacy recovery), and
2. **drops every `custom` key that is neither referenced by an entry nor a chart name.**
So a custom account disappears once no entry uses it **[Tested]**.

---

## 7. Startup Lifecycle

`if __name__ == "__main__"` creates `tk.Tk()`, then `App(root)`, then `root.mainloop()`. Inside `App.__init__`, in this order:

1. Set title, size (1280x760, min 1000x600); try `root.state('zoomed')` (ignored where unsupported).
2. Build the menu bar (see §12).
3. Initialize `entries=[]`, `custom={}`, `ws_rows=[]`, `ledger_cache={}`.
4. `self.load()` — may show error dialogs; see §10.
5. `self.set_style()` — applies the `clam` theme and all named styles.
6. Bind `<F5>` to `refresh`.
7. Create the notebook, then `build_journal`, `build_ledger`, `build_worksheet` (this order defines tab indexes 0, 1, 2).
8. `self.refresh()`.

`build_journal` also binds `Ctrl+F` (focus search) and `Ctrl+N` (new entry) on the root window.

---

## 8. The Refresh Lifecycle

`App.refresh()` (in `main.py`) is the **single path** that brings every screen up to date:

1. Rebuild Journal debit/credit dropdown values from `all_account_names()`.
2. Rebuild the Ledger dropdown (`"All Accounts"` + names); keep the current selection if it still exists, else reset to "All Accounts".
3. `ledger_cache.clear()`.
4. `refresh_journal()` → `apply_search_filter()` → `refresh_journal_with_filter()` → `JournalTable.set_rows()`.
5. `refresh_ledger()` → clears the Treeview and re-renders.
6. `refresh_worksheet()` → `compute_worksheet()` → stores `ws_rows` → `GridTable.set_rows()`.
7. `clear_journal_form()` — clears and **locks** form fields, hides Cancel/Delete buttons, resets the "Add Entry" label, clears the status text, sets `_editing_index = None`.

Consequences to remember:
- Pressing **F5 / View > Refresh while editing an entry discards the edit** (step 7).
- `clear_journal_form()` now correctly resets `v_month`, `v_day`, `v_year` to today (fixed; previously referenced non-existent `v_date`).

### The mutation sequence (do not reorder)

Both places that change `entries` follow the same order:

```text
change self.entries  ->  sync_custom_accounts()  ->  save()  ->  refresh()
```

- `add_entry` (add and edit-update) and `delete_multiple_entries` are the **only** callers of `save()`. `load()` is called only at startup.
- Since `refresh()` always recomputes Ledger and Worksheet from `entries`, views never need to be patched individually.

---

## 9. Feature Flows

### 9.1 Journal (`journal_tab.py`, `journal_table.py`)

**Form and lock/unlock.** Fields start locked (Comboboxes `disabled`, Entries `readonly`). A click unlocks one field
(and re-locks the others); focus-out or a click on the panel locks all. This click-to-unlock behavior is intentional
and must be preserved. `Enter` in any field calls `add_entry`.

**Validation** (`_validate_form`, in this order): valid calendar date → debit not empty → credit not empty →
debit ≠ credit (case-insensitive, whitespace-normalized) → amount present, finite, `> 0` (commas, `₱` and `$` are stripped) →
amount quantized to 2 decimals. Errors show in `status_var` and tint the field for 3 seconds.

**Add / edit.** `add_entry` validates → `resolve()` both accounts (may open the type dialog) → builds the entry →
either appends, or replaces `entries[_editing_index]` → mutation sequence (§8).
Edit mode is entered by double-clicking a debit/credit line; the button becomes "Update Entry" and Cancel/Delete appear.

**Delete.** `delete_multiple_entries(indices)` asks for confirmation, deletes in reverse index order, runs the mutation
sequence, then clears the table's selection. It reaches into `JournalTable` private attributes (`_selected_iids`,
`_anchor_iid`, `_rows`), so the two files are tightly coupled.

**Search.** Case-insensitive substring match over debit, credit, description, displayed date, and amount; results sorted
by `(date, index)`; `search_info` shows counts.

**Table model.** `refresh_journal_with_filter` converts entries to `JournalTable` rows `(entry_idx, line_type, values, tags)`:
`debit` line (date, debit account, amount in Dr), `credit` line (indented account, amount in Cr), optional `desc` line,
and a `separator` between entries. The row id is `f"{entry_idx}_{line_type}"`, where **`entry_idx` is the position in
`App.entries`, not the on-screen position**. Anything that changes indexes must clear the table selection.
Ctrl+click, Shift+click or Ctrl+A switch the table into checkbox "selection mode" (a header "select all" checkbox then appears); it leaves that mode when nothing is selected.
Callbacks wired by `JournalMixin`: `bind_select`, `bind_edit`, `bind_context`, `bind_delete`.

### 9.2 Ledger (`ledger_tab.py` + `App._compute_account_ledger`)

- `_compute_account_ledger(name)` lives in **`main.py`** (the duplicate formerly in `ledger_tab.py` was removed). It walks `entries` in order and
  returns `(lines, balance, sum_dr, sum_cr)`; each line is `(date, particulars, dr, cr, running_balance)`.
  Balance = running `debit − credit` (Dr-positive). Particulars = the description, or the *other* account's name if the description is empty, plus `"  [Adj]"` for adjusting entries.
  **Since 2026-11-21 (§5.1):** blank descriptions are stored as `""`, so the *other-account* fallback now works for new form entries. Existing entries that still contain the old placeholder text `"[wala ni enter ug description]"` are left unchanged and show that text.
- `refresh_ledger()` renders either **All Accounts** (one group per account that has activity: a bold header row, its lines, a `Subtotal` row) or a **single account** (lines plus a `TOTALS` row). An empty selection shows a friendly empty-state message.
- **The on-screen Ledger shows no per-line running balance (T-account format).** The Balance cell is filled only on `Subtotal`/`TOTALS` rows (via `balfmt`, e.g. `1,000 Dr`). The per-line running balance is computed but only appears in the Ledger CSV — **intentional per instructor's format**.
- Adjusting rows are tinted by testing whether the text `"[Adj]"` appears in the particulars string, so the marker text is part of the display contract.
- `ledger_cache` is filled lazily per account and cleared only by `App.refresh()`. Changing the dropdown re-renders from the cache.

### 9.3 Worksheet (`worksheet_tab.py`, `grid_table.py`)

`compute_worksheet()` returns `(rows, ok)`. Column indexes (also the order of `HEADS`):

| 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| TB Dr | TB Cr | ADJ Dr | ADJ Cr | ATB Dr | ATB Cr | IS Dr | IS Cr | OE Dr | OE Cr | BS Dr | BS Cr |

Algorithm **[Tested]** (all arithmetic in `Decimal`):

1. For every account in `get_all_account_names()`, total Dr and Cr separately for regular entries (`tb`) and `adj` entries (`adj`).
2. Per account: `tnet = TB Dr − TB Cr`; `anet = tnet + ADJ Dr − ADJ Cr`.
   Columns 0–1 = `tnet` split into Dr (positive) or Cr (negative); columns 2–3 = the adjustment totals; columns 4–5 = `anet` split the same way.
3. Copy columns 4–5 into the statement section chosen by `SECTION_COL[SECTION[type]]` (IS, OE or BS). Other statement columns stay blank.
4. Row tags: alternating `""`/`"odd"` for accounts. Every account is listed, even with no activity.
5. **TOTAL** row: sum of each of the 12 columns.
6. **NET INCOME / NET LOSS** row: `ni = total[7] − total[6]` (IS Cr − IS Dr). If `ni ≥ 0`: label *NET INCOME*, value in IS Dr (6) and OE Cr (9). Otherwise *NET LOSS*, value in IS Cr (7) and OE Dr (8).
7. **ENDING OWNER'S CAPITAL** row: `ec = (OE Cr total + NI's OE Cr) − (OE Dr total + NI's OE Dr)`. If `ec ≥ 0`: value in OE Dr (8) and BS Cr (11); otherwise in OE Cr (9) and BS Dr (10).
8. **GRAND TOTAL** row: columns 6–11 = TOTAL + NET row + ENDING CAPITAL row.
9. `ok` = six booleans (`TB, ADJ, ATB` compare the TOTAL row's Dr/Cr; `IS, OE, BS` compare the GRAND TOTAL row's Dr/Cr).
   **`refresh_worksheet()` discards `ok`**, so no balance indicator is displayed anywhere today.

Row count = number of accounts + 4 (TOTAL, NET row, ENDING CAPITAL, GRAND TOTAL).
Because Accumulated Depreciation is typed *Asset* in `CHART`, its credit balance lands in BS Cr; the classification is per account type, not per balance side.

`refresh_worksheet()` stores the raw rows in `App.ws_rows` (Decimal/None cells, used by exports) and passes `fmt()`-formatted strings to
`GridTable.set_rows([(label, [12 strings], tag)])`. `GridTable` supports tags `""`, `"odd"`, `"total"`, `"grand"`,
stretches the number columns on resize (minimum 80 px), and draws thick lines around each Dr/Cr pair.

---

## 10. Persistence and Recovery (`data.py`)

**Load behavior [Tested]**

| Situation | Result |
|---|---|
| File missing | Silent; starts empty (normal first run) |
| Invalid JSON | Error dialog "Data File is Corrupted"; app starts with **empty in-memory data**; file untouched *at load time* |
| JSON is not an object, or `entries` not a list, or `custom` not a dict | Dialog "Invalid Data Format"; app starts with empty data |
| Some individual entries malformed (bad date, empty debit/credit, invalid amount) | Skipped silently; one warning dialog shows count of skipped entries ("Data Load Warning") |
| `PermissionError` / other exception | Error dialog; empty in-memory data |

**Save behavior.** `save()` first builds the JSON text of the NEW data, then `_create_backup(new_content)` writes that new content as the backup (skipped if identical to the newest backup), then the temp file + `os.replace` writes the real data file. So each backup is a copy of the data AS SAVED, not a copy of the file from before the save. The newest backup normally equals the current data file; to go back one step, use the second newest backup. `MAX_BACKUPS = 20`; older backups are deleted by name order. Identical consecutive saves do not create duplicate backups. If the data file was unreadable on load (`load_failed = True`), it is copied to `accounting_data.unreadable.<timestamp>.json` instead of a normal backup, and these files are never removed by `_cleanup_old_backups`. A backup failure is ignored and the save continues. Save errors (permission, disk full, read-only, other) show dialogs; they do not retry.

**Additional persistence risks found in the 2026-11-20 review (§13 #15-#18):**

- `save()` wrote straight into `accounting_data.json` (no temporary file followed by a rename), so a crash or power loss in the middle of a write could leave a truncated file. **FIXED 2026-11-21** — now uses temp file + `os.replace` atomic swap.
- `load()` accepts an entry whose `amount` is not a number. The first `refresh()` then raises `decimal.InvalidOperation` and the app closes at startup with no dialog **[FIXED 2026-11-20 — _validate_data now validates amount]**.
- Backup names have one-second resolution and only 5 are kept, so the recovery window is the last 5 saves. Saves within the same second share one backup file (9 rapid saves left 1 backup) **[FIXED 2026-11-21 — now microsecond resolution, MAX_BACKUPS=20, duplicate-save skip, unreadable.* protection]**.

---

## 11. UI Layer

- **`style.py`** holds all design tokens (long names `COLOR_*`, `SPACE_*`, `TEXT_*` plus short aliases `BG`, `SP2`, `F_XS`, `ROW_H`, …) and
  `StyleMixin.set_style()`, which applies the `clam` theme and the named styles (`Primary/Ghost/Danger.TButton`, `Panel/Card.TFrame`,
  `Muted/Title/Subtitle/Heading/FieldLabel/Error/Success.TLabel`, `Error.TEntry`, `Error.TCombobox`, notebook, scrollbars).
  Token values are documented in `DESIGN.md`.
- **Two table technologies are used.** The Ledger uses a styled `ttk.Treeview` built by `make_tree()` (row tags `odd, adj, total, grand, empty, acct, credit_line, desc_line`).
  The Journal and Worksheet use **custom Canvas tables** (`JournalTable`, `GridTable`) that draw their own rectangles/lines/text, so
  `ttk` style changes do **not** reach them; they read tokens from `style.py` directly.
- Some values are hard-coded and will not follow token changes: `#DBEAFE`/`#2563EB`/`#000000` and `"Segoe UI"` fonts inside `journal_table.py`,
  `small_bold` font in `grid_table.py`, and blue hex colors in the Excel/PDF export code.
- Changing a shared style or token can affect Journal, Ledger and Worksheet at once; inspect all three.

---

## 12. Menus, Shortcuts and Export Routing

| Menu item | Handler | Notes |
|---|---|---|
| File > Export > Export CSV | `App.export_csv` | Dispatches on the active tab: 0 → `export_journal_csv`, 1 → `export_ledger_csv`, 2 → `self.export_worksheet_csv()` |
| File > Export > Export Excel / Export PDF | `WorksheetMixin.export_excel` / `export_pdf` | Always export the **Worksheet** (`ws_rows`), whichever tab is open |
| File > Exit | `root.quit` | |
| Edit > New Entry (Ctrl+N) | `focus_new_entry` | Switches to Journal and opens the debit box |
| Edit > Delete Entry | `delete_selected_entry` | Journal tab only; other tabs show an info message |
| View > Refresh (F5) | `refresh` | See §8 |
| Tools > Validate Data | `App.validate_data` | Read-only report on missing accounts, debit = credit, bad/≤0 amounts. (Not the same as `DataMixin._validate_data`.) |
| Tools > Backup Manager… | `show_backup_manager` | Lists up to 10 backup file names; **no restore function** |
| Help > Keyboard Shortcuts | `show_shortcuts` | Static text dialog |
| Help > About | `about_tab.show_about` | Modal dialog |

Other bindings: `Ctrl+F` (Journal search), Journal table keys `Delete`, `Ctrl+A`, `Escape`, Ctrl/Shift+click (these are bound on the table canvas, so they need focus there).
The "Del" text in the Edit menu label is display text only; there is no root-level `<Delete>` binding.

Export formats:
- **Journal CSV** — Date (display format), Debit, Credit, Amount (stored string), Description, Adjusting Yes/No; insertion order.
- **Ledger CSV** — follows the Ledger's current selection; includes the per-line running balance; totals rows use `fmt()` (not `balfmt()`), so the sign/`Dr`/`Cr` wording differs from the screen.
- **Worksheet CSV / Excel / PDF** — built from `ws_rows`. Excel writes values with `float()` and static formatting (no formulas, despite the docstring). PDF is landscape Letter. Missing `openpyxl`/`reportlab` produces a "Missing Library" message.

### 12.1 Worksheet CSV export — **FIXED (2026-11-17 merge, renamed 2026-11-21)** **[Tested]**

`App.export_csv` overrides `WorksheetMixin.export_csv` (§3). On the Worksheet tab the dispatcher **formerly** called `self.export_csv()`, which is itself,
causing `RecursionError`. The Worksheet tab's own **Export CSV** button (`command=self.export_csv`) hit the same path.

**Fix applied in `main.py:196-197` (2026-11-17):** the Worksheet branch now explicitly calls `WorksheetMixin.export_csv(self)` instead of `self.export_csv()`.
The intended target is now reached directly, avoiding the MRO collision.

**Renamed 2026-11-21 (Task 5 Part B):** `WorksheetMixin.export_csv` → `export_worksheet_csv` in `worksheet_tab.py` (definition and button command).
The dispatcher in `main.py` now calls `self.export_worksheet_csv()`. The name collision is eliminated; the Worksheet export is reachable directly.
The Worksheet tab's own **Export CSV** button (`command=self.export_worksheet_csv`) now calls `export_worksheet_csv` directly — it does **not** go through the dispatcher.

**Re-verified 2026-11-21 [Tested, Tkinter stubbed]:** with the Worksheet tab active, `App.export_csv` calls `self.export_worksheet_csv()` without recursion. The Worksheet tab's own *Export CSV* button also calls `export_worksheet_csv` directly.

---

## 13. Known Issues and Code Observations

Recorded so future work does not rediscover them. **Items marked FIXED were resolved during the merge with the team member's visual redesign branch.** Do not "fix" an item unless the user asks; anything touching accounting, persistence, or exports needs the checks in `AI_GUIDE.md`.

| # | Where | Observation | Evidence |
|---|---|---|---|
| 1 | `main.py` export dispatch | Worksheet CSV export recurses infinitely (§12.1). **FIXED 2026-11-17** — now calls `WorksheetMixin.export_csv(self)` directly; **FIXED 2026-11-21** — renamed to `export_worksheet_csv`, name collision eliminated. | Tested |
| 2 | `journal_tab.py` `refresh` | Dead duplicate of `App.refresh`. **RESOLVED** - the method no longer exists (searched 2026-11-20). | Read |
| 3 | `journal_tab.py` `_create_context_menu` | Never called, so `self.ctx_menu` is never created. **FIXED** — now called in `build_journal()`. | Read |
| 4 | `data.py` `load()` | In the invalid-JSON dialog, the last string segment lacks an `f` prefix, so `{backup_msg}` is shown literally. **FIXED** — f-string prefix added. | Tested |
| 5 | `data.py` `load()`/`save()` | After a failed load the next save overwrites the unreadable file; the corrupt copy becomes a backup and can push older good backups out of the 5-file window. | Tested |
| 6 | `data.py` `load()` | "Invalid Data Format" dialog says valid entries will be kept, but the code then starts with empty data. | Tested |
| 7 | `worksheet_tab.py` | Balance flags `ok` are computed and discarded; no on-screen balanced/unbalanced indicator. | **ON HOLD** — deferred per product decision |
| 8 | `ledger_tab.py` / `main.py` | Screen shows no per-line running balance; Ledger CSV totals use `fmt()` while the screen uses `balfmt()`. Ledger order is insertion order, not date order. | **INTENTIONAL** — follows instructor's T-account format (balance only on Subtotal/TOTALS rows). CSV retains running balance for advanced use. |
| 9 | `journal_tab.py` `add_entry` | If the user cancels the type dialog for the *credit* account after the *debit* account was already added as custom, that custom account stays in `custom` until the next `sync_custom_accounts()`. | **FIXED** — `resolve()` no longer mutates `self.custom`; both accounts added atomically after both resolve |
| 10 | `journal_tab.py` `_show_success` | The "Entry added/updated" message is set, then cleared immediately by `refresh()` → `clear_journal_form()`. | Read |
| 11 | `main.py` `clear_journal_form` | **FIXED** — now resets `v_month`, `v_day`, `v_year` to today. Previously referenced non-existent `v_date`. | Fixed |
| 12 | `worksheet_tab.py` Excel export | Converts `Decimal` to `float` for the file (display/export only; calculations remain `Decimal`). | Read |
| 13 | `grid_table.py` `set_rows` | Tags `""` and `"odd"` use the same background, so account-row striping is not visible. | Read |
| 14 | — | (Item removed — claims were incorrect. `fmt_amt` defined once in `style.py` and imported; `fmt_tree`, `constants.FONT`, `constants.date_to_iso` never existed; `preserve_selection` is actively used.) | — |
| 15 | `data.py` `save()` | **High.** The data file is written in place (`open(DATA_FILE, "w")` then `json.dump`), not via a temporary file and `os.replace`. A crash, power loss or full disk during the write can leave truncated JSON, which is exactly the corrupt-file situation in #5. | **FIXED 2026-11-21** — `save()` now builds JSON text first, writes to `DATA_FILE.tmp`, calls `flush()` + `os.fsync()`, then `os.replace()` for atomic swap. Temp file cleaned up on any error. Existing error dialogs unchanged. | Tested |
| 16 | `data.py` `_validate_data`, `main.py` `refresh()` | **High.** The load validator only checks that `date`, `debit`, `credit`, `amount` exist. An entry with a non-numeric `amount` (or non-string account names) is kept, then `compute_worksheet` and `_compute_account_ledger` raise `decimal.InvalidOperation` during the first `refresh()` in `App.__init__`. The app closes at launch with no dialog, and *Validate Data* can never be reached to find the bad entry. | **FIXED 2026-11-20** — `_validate_data` now validates amount (Decimal, finite, >0), date format, non-empty debit/credit strings, coerces `adj` to bool, normalizes amount to 2-decimal string. Shows warning dialog with count of skipped entries. | Tested |
| 17 | `data.py` `_create_backup` | **Medium.** One backup per save, named with 1-second resolution, only the newest 5 kept. The recovery window is the last 5 saves (minutes of editing). Saves within the same second overwrite the same backup file (9 rapid saves left 1 backup). Backups are copies made *before* the save, so after a bad load plus save the newest backup is the unreadable file (#5). | **FIXED 2026-11-21** — microsecond resolution prevents overwrites; `MAX_BACKUPS=20`; identical consecutive saves skip backup; unreadable file preserved as `accounting_data.unreadable.<timestamp>.json` and never cleaned up. **Note:** backups now contain the NEW data as saved, not the previous file — the newest backup equals the current data file; to go back one step use the second newest. | Tested |
| 18 | `.gitignore` / repo contents | **Medium.** `.gitignore` lists only `accounting_data.json`, so `accounting_data.backup.*.json` files (real student data) are committed; the ZIP contains five. `.claude/skills/impeccable/` (including a Windows `.exe`) and `.impeccable/` are also committed although they are not runtime code. | **FIXED 2026-11-21** — .gitignore now ignores accounting_data.backup.*.json, accounting_data.unreadable.*.json, accounting_data.json.tmp, and .claude/. .impeccable/ intentionally stays tracked (DESIGN.md references .impeccable/surfaces/ledger-tab.md). Files already committed need `git rm --cached` by the human. | Read |
| 19 | `journal_tab.py` `add_entry` | **Medium.** A blank description is stored as `[wala ni enter ug description]`. Because it is non-empty, the Ledger's "other account" fallback never applies to form entries, and the placeholder appears in the Ledger and in every export that a student may submit. Whether to keep, translate or leave it blank is a product decision. | **FIXED 2026-11-21** — blank descriptions now stored as empty string `""`; Ledger fallback works for new entries; CSV/Excel/PDF exports show empty cell; old entries with placeholder preserved unchanged. | Tested |
| 20 | `data.py` `save()` and its callers | **Low.** `save()` catches every error, shows a dialog and returns `None`. `add_entry` and `delete_multiple_entries` cannot tell that the save failed, so they still refresh and show the change; the data exists only in memory until a later save succeeds. | **FIXED 2026-11-21** — `save()` now returns True on success, False on failure. `add_entry` and `delete_multiple_entries` take deepcopy snapshots before changes; on save failure they restore the snapshots, refresh, keep the form/selection as-is, and do not show a success message. | Tested |
| 21 | `data.py` `load()` | **Low.** `UnicodeDecodeError` is a subclass of `ValueError`, so a data file that is not valid UTF-8 is reported by the "Invalid Data Format" dialog (#6) instead of a clear encoding message. | Read |
| 22 | `README.md` | **Low.** The file held only the heading `# Accounting_Group3`. **Addressed 2026-11-20** (documentation only): it now explains purpose, how to run, data and backups, layout and the other documents. | Read |

**Suggested order if these are fixed (not applied; each touches persistence or validation, so follow the checks in `AI_GUIDE.md`):** #16 (validate amount, dates and account names on load, and report skipped entries) **FIXED 2026-11-20**, #15 (atomic write) **FIXED 2026-11-21**, #5/#17 (do not overwrite an unreadable file; keep more or timestamp-unique backups) **FIXED 2026-11-21**, #19 (blank description stored as empty string) **FIXED 2026-11-21**, #1 (export_csv rename / duplicate methods) **FIXED 2026-11-21**, #20 (save returns False on failure; callers undo on failure) **FIXED 2026-11-21**, then #18.

---

## 14. Change Impact Guide

| If you change… | Also inspect / re-test |
|---|---|
| An entry field or its meaning | `_validate_data`, `save/load`, `add_entry`, `edit_entry`, Journal rows, `_compute_account_ledger`, `compute_worksheet`, all CSV/Excel/PDF exports, `validate_data` |
| `CHART`, `SECTION`, `SECTION_COL`, `HEADS` | `types()`, `compute_worksheet` totals and all six balance checks, Ledger, Worksheet exports |
| Account-name helpers or `sync_custom_accounts` | Journal dropdowns, Ledger dropdown, Worksheet rows, load and delete behavior for custom accounts |
| `refresh()` or the save→refresh order | Every tab, `ledger_cache` invalidation, edit-mode reset, F5 behavior |
| `_compute_account_ledger` | Ledger screen, Ledger CSV, `ledger_cache` consumers |
| `compute_worksheet` | `ws_rows` consumers (CSV, Excel, PDF), `GridTable` rows, net income/loss and ending-capital logic |
| `JournalTable` row format or iid scheme | `refresh_journal_with_filter`, selection, edit, delete, selection toolbar |
| `style.py` tokens or styles | Journal, Ledger, Worksheet, About dialog, hard-coded copies in canvas tables and exports |
| Method names in any mixin | MRO collisions (§3) |
| Export code | Journal, Ledger, Worksheet paths separately; missing optional library path |

---

## 15. How This Document Was Verified

**Done:** read all ten Python files completely; read `AI_GUIDE.md`, `DESIGN.md`, the previous `ARCHITECTURE.md`, `MEMORY.md`,
and `SESSION_HANDOFF.md` for consistency; `python -m py_compile` on all `.py` files (passed); with `tkinter` replaced by a stub
and **synthetic data in a temporary folder** (the real data file and backups were not used or modified), tested: method resolution,
the Worksheet CSV recursion, worksheet math (net income, net loss, drawings, adjusting entries, legacy accounts), custom-account sync,
Ledger ordering, and every `load()`/`save()`/backup path.

**GUI launched and verified post-merge:** application starts successfully; visual layout confirmed (seamless light-gray background across root/notebook/tabs, thin `BORDER_STRONG` separators between sections, compact spacing per updated scale, labels blend into panel background, Worksheet tab title left + exports right, Journal table PRIMARY header with empty state icon, Ledger fixed-height top bar, About dialog two-column layout).

**Not done:** exercising click-to-unlock, selection, right-click, dialogs, or the Excel/PDF exports with real data. Items labeled **[Read]** should be confirmed interactively before anyone relies on them.

**2026-11-20 review [Tested, Tkinter stubbed, on a copy of the code with synthetic data in temporary folders; the five backup JSON files were only read]:** all ten modules compile; Worksheet math balances on all five backup datasets (all six checks true); a non-numeric amount crashes both the Worksheet and the Ledger computation (#16); the form-entered blank description appears as the Cebuano placeholder in Ledger particulars (#19); a truncated data file loads as empty and the next save leaves the unreadable copy as the newest backup (#5, #17); 9 saves within one second leave 1 backup (#17); a failed save shows a dialog and returns `None` (#20); the Worksheet tab dispatch reaches `WorksheetMixin.export_csv` without recursion (§12.1). The GUI could not be launched in that environment (Tkinter was not installed), so the 2026-11-17 GUI verification above is unchanged.

Update this file whenever module responsibilities, shared state, the refresh sequence, the data model, or the issues in §13 change.
