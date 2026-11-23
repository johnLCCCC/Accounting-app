# Design System

> **Purpose:** This document is the shared visual source of truth for the Accounting application.
> It is written for developers and AI assistants making UI/UX changes.
>
> **Implementation authority:** `style.py` contains the currently implemented theme tokens and ttk styles.
> This document records those values, explains how they should be used, and sets rules for future
> design changes. If this document and the code disagree, inspect `style.py`, identify the mismatch,
> and update the documentation or implementation deliberately. Do not silently assume either is current.

---

## 1. Product and Design Intent

The application is a desktop accounting-learning tool. Its interface should feel:

- **Calm and trustworthy:** use restrained color, clear labels, and predictable interactions.
- **Easy to scan:** make account names, dates, descriptions, amounts, and totals easy to distinguish.
- **Data-focused:** tables may contain many rows, so avoid decoration that competes with the accounting information.
- **Consistent:** Journal, Ledger, Worksheet, and supporting screens should feel like parts of one application.
- **Practical:** prioritize legibility, useful density, and reliable desktop interaction over visual effects.

The established direction is a **clean, light, blue-accented interface** with neutral surfaces, subtle borders, and semantic status colors.

Do not introduce a new visual direction for an individual screen unless the task explicitly requests a redesign of the overall design language.

## 2. Platform and Implementation Constraints

- This is a **Python Tkinter/ttk desktop application**, not a web application.
- Prefer existing ttk widgets, existing canvas/table implementations, and shared project helpers.
- Do not introduce browser-only concepts or CSS properties as if they were directly available in Tkinter.
- Tkinter/ttk styling differs by widget, theme, and operating system. A style setting that works for one widget may not work identically for another.
- Avoid adding external UI dependencies or replacing the widget toolkit unless explicitly approved.
- Do not add shadows, rounded corners, animated transitions, or other effects that the current toolkit cannot reliably support. Use restrained borders, spacing, typography, and color to create hierarchy instead.

### Source-of-truth files

| File | Responsibility |
| --- | --- |
| `style.py` | Implemented color, spacing, typography tokens; shared ttk styles; Treeview builder and row tags |
| `constants.py` | Application constants used by the rest of the project |
| `main.py` | Main window and notebook/tab composition |
| `journal_tab.py`, `ledger_tab.py`, `worksheet_tab.py` | Screen-specific UI composition |
| `journal_table.py`, `grid_table.py` | Table implementations and related presentation behavior |
| `.impeccable/surfaces/` | Screen-specific design briefs and decisions |

When changing a shared style, search for its use across the project first. A shared style change can affect multiple screens.

## 3. Design Tokens

The following values are defined in `style.py`. Use the existing constants rather than repeating raw values in new code.

### 3.1 Color palette

| Token / constant | Value | Intended use |
| --- | --- | --- |
| `COLOR_BG` | `#FFFFFF` | Main and primary content surfaces |
| `COLOR_BG_ALT` | `#F8FAFC` | Subtle alternate surfaces and table striping |
| `COLOR_BG_PANEL` | `#F1F5F9` | Grouped form and panel backgrounds |
| `COLOR_BORDER` | `#E2E8F0` | Subtle borders and separators |
| `COLOR_BORDER_STRONG` | `#CBD5E1` | More visible borders and emphasis |
| `COLOR_TEXT` | `#1E293B` | Primary text |
| `COLOR_TEXT_MUTED` | `#64748B` | Secondary labels, hints, and supporting text |
| `COLOR_TEXT_INVERTED` | `#FFFFFF` | Text on strong filled-color controls |
| `COLOR_PRIMARY` | `#2563EB` | Primary actions and selected/active emphasis |
| `COLOR_PRIMARY_HOVER` | `#173AA5` | Hover state for primary actions |
| `COLOR_PRIMARY_LIGHT` | `#DBEAFE` | Selected rows and emphasized totals |
| `COLOR_PRIMARY_FOCUS` | `#93C5FD` | Focus accent where supported |
| `COLOR_SUCCESS` | `#059669` | Successful or positive feedback |
| `COLOR_SUCCESS_LIGHT` | `#D1FAE5` | Soft success background where needed |
| `COLOR_DANGER` | `#DC2626` | Errors and destructive actions |
| `COLOR_DANGER_LIGHT` | `#FEE2E2` | Error/validation background |
| `COLOR_WARNING` | `#D97706` | Warning and adjusting-entry semantics |
| `COLOR_WARNING_LIGHT` | `#FEF3C7` | Soft warning/adjusting-entry background |
| `COLOR_ACCENT` | `#0E7490` | Output and overview actions (exports, counters, ledger headings) |
| `COLOR_ACCENT_HOVER` | `#155E75` | Hover state for accent actions |
| `COLOR_ACCENT_PRESSED` | `#164E63` | Pressed state for accent actions |
| `COLOR_ACCENT_LIGHT` | `#ECFEFF` | Pale teal background for ledger account headings |

**Color rules**

1. Use the semantic token that matches the meaning; do not use success green merely as decoration.
2. Reserve primary blue for important actions, selected states, and meaningful emphasis.
3. Use neutral surfaces for most of the interface. Large areas of saturated color should be avoided.
4. Do not communicate a status through color alone. Pair color with text, a label, an icon, or another clear cue.
5. Keep text readable against its background. Do not invent lighter text colors for important information without checking contrast.
6. If a reusable color is added, define it in `style.py` and document it here.
7. **Accent teal marks output and overview elements (exports, counters, ledger account headings). It is never used for success, error, warning or selection, and never as the only cue.**

### 3.2 Typography

Typography constants currently defined in `style.py`:

| Constant | Current definition | Intended role |
| --- | --- | --- |
| `FONT_UI` | `Segoe UI` | Main interface typeface |
| `TEXT_XS` | 11 px | Dense secondary information, table cell values |
| `TEXT_SM` | 12 px | Supporting labels and table text |
| `TEXT_BASE` | 14 px | Default interface text |
| `TEXT_LG` | 16 px, bold | Small headings and emphasized labels |
| `TEXT_XL` | 18 px, bold | Larger headings |
| `TEXT_2XL` | 22 px, bold | Screen title |
| `F_MONO` | `Consolas`, 12 px | Monospaced amount/input use |

Typography guidance:

- Use the existing font constants wherever possible.
- Keep screen titles visibly stronger than section headings, and section headings stronger than field labels.
- Use muted text for secondary information, not for essential values or instructions.
- Use monospaced type only where fixed-width digits improve comparison or entry.
- Keep table text compact enough for data density but readable at normal desktop viewing distance.
- Consider font availability on the target Windows environment; provide a sensible fallback if a new font is proposed.

### 3.3 Spacing

The spacing scale uses a 4 px base, compacted to a middle ground between the original generous spacing and the team's tight redesign:

| Constant | Value | Note |
| --- | ---: | --- |
| `SPACE_1` / `SP1` | 4 px | Base unit |
| `SPACE_2` / `SP2` | 6 px | Compact intra-element gaps |
| `SPACE_3` / `SP3` | 10 px | Standard gaps, card padding |
| `SPACE_4` / `SP4` | 14 px | Section gaps, table cell padding |
| `SPACE_5` / `SP5` | 16 px | Card padding (vertical), form row gaps |
| `SPACE_6` / `SP6` | 18 px | Major section separation, page margins |
| `SPACE_8` / `SP8` | 24 px | Top-level container padding |

Spacing guidance:

- Use the scale rather than arbitrary one-off spacing values when practical.
- Use smaller gaps for tightly related controls and larger gaps to separate sections.
- Keep alignment consistent across neighboring forms, toolbars, and tables.
- Avoid both cramped controls and excessive whitespace that pushes important accounting data below the visible area.
- Existing screen-specific spacing may differ; inspect the relevant screen before changing it.

### 3.4 Table dimensions

| Constant | Current value |
| --- | ---: |
| `TABLE_ROW_HEIGHT` / `ROW_H` | 28 px |
| `TABLE_HEADER_HEIGHT` / `HEAD_H` | 32 px |

These are the shared defaults in `style.py`. A specialized table may have its own implementation or dimensions; do not assume every table uses `make_tree()`.

Spacing guidance:

- Use the scale rather than arbitrary one-off spacing values when practical.
- Use smaller gaps for tightly related controls and larger gaps to separate sections.
- Keep alignment consistent across neighboring forms, toolbars, and tables.
- Avoid both cramped controls and excessive whitespace that pushes important accounting data below the visible area.
- Existing screen-specific spacing may differ; inspect the relevant screen before changing it.

### 3.4 Table dimensions

| Constant | Current value |
| --- | ---: |
| `TABLE_ROW_HEIGHT` / `ROW_H` | 30 px |
| `TABLE_HEADER_HEIGHT` / `HEAD_H` | 34 px |

These are the shared defaults in `style.py`. A specialized table may have its own implementation or dimensions; do not assume every table uses `make_tree()`.

---

## 4. Shared Component Standards

These standards describe the intended use of existing styles. Before adding or changing a style, inspect its actual configuration and usage in `style.py`.

### 4.1 Buttons

| Style | Intended role | Usage rule |
| --- | --- | --- |
| `Primary.TButton` | Main action in a local context | Use sparingly; make the most important action visually clear |
| `Ghost.TButton` | Secondary or low-emphasis action | Use for actions that should remain available without competing with the primary action |
| `Danger.TButton` | Destructive action | Reserve for deletion or other destructive operations |
| `TButton` | Default button | Use when no stronger semantic role is needed |
| `WorksheetExport.TButton` | Worksheet export actions | Accent teal export buttons in Worksheet tab |
| `Worksheet header` | Worksheet header: white (BG) with bold TEXT, BORDER_STRONG separators and a 2 px PRIMARY line underneath; body rows use BG_PANEL so the header is distinguished by contrast, not by a color fill. Total rows stay white; the grand total row uses PRIMARY_LIGHT. | Worksheet table header styling |

Button guidance:

- Use clear, action-oriented labels (for example, "Save entry" rather than "OK" when context is not obvious).
- Avoid presenting several neighboring buttons with equal visual emphasis.
- Keep related buttons aligned and consistently spaced.
- Do not use the danger style for ordinary cancellation or navigation.
- Preserve keyboard access and existing command bindings.
- Do not claim a hover, focus, or disabled treatment exists without checking the actual ttk style and platform behavior.

### 4.2 Text fields and comboboxes

Existing styles: `TEntry`, `Error.TEntry`, `TCombobox`, `Error.TCombobox`, `LedgerFilter.TCombobox`.

Guidance:

- Keep labels visible; do not rely on placeholder text as the only field label.
- Align related fields and use consistent widths when their content types are comparable.
- Make validation errors specific and place them close to the affected field.
- Use error styling together with an explanatory message; color alone is insufficient.
- Preserve the application's existing field-locking behavior: fields are intentionally locked until clicked and return to their locked state on focus loss.
- Preserve existing validation, focus handling, keyboard behavior, and data bindings.

### 4.3 Panels, cards, and grouped sections

Existing styles include `Panel.TFrame`, `Card.TFrame`, and `Section.TLabelframe`.

Guidance:

- Use panels to group related controls, not to put a box around every individual widget.
- Use `Card.TFrame` for the shared bordered table container created by `make_tree()`.
- Use section labels when they help users understand the purpose of a group.
- Maintain consistent inner padding and alignment within repeated panels.
- Avoid nested borders that make the interface visually heavy.

### 4.4 Tabs and navigation

The main notebook contains the Journal, Ledger, and Worksheet tabs.

Guidance:

- Keep tab labels clear and consistent.
- Preserve the established blue selected-state emphasis and neutral inactive states.
- Do not change tab order, navigation behavior, or screen construction as part of a design-only task unless explicitly requested.
- Ensure a redesigned tab remains recognizable as an interactive navigation control.

### 4.5 Tables and accounting data

Tables are a primary part of this application and must prioritize accuracy, scanning, and comparison.

For standard ttk tables, use the shared `StyleMixin.make_tree()` helper when appropriate. It provides a bordered container, a `Treeview`, scrollbars, column alignment, and semantic row tags.

Existing semantic tags configured by `_configure_tree_tags()`:

| Tag | Established meaning |
| --- | --- |
| `odd` | Alternate/striped row |
| `adj` | Adjusting entry |
| `total` | Total row |
| `grand` | Grand total / strongest total emphasis |
| `empty` | Empty-state row |
| `acct` | Account/group row |
| `credit_line` | Credit-line typography |
| `desc_line` | Supporting description line |

Table rules:

- Align dates and descriptive text left.
- Align numeric amounts right so digits are easy to compare.
- Preserve the existing accounting convention that zero or absent amounts may display as blank.
- Use semantic tags consistently; do not repurpose a tag for a different meaning.
- Keep totals visually distinct from ordinary transaction rows without making them overpower the table.
- Use warning treatment for adjusting entries and primary-light treatment for grand totals, consistent with existing tags.
- Preserve sorting, selection, scrolling, row identity, and all table callbacks.
- Avoid unnecessary vertical gridlines and heavy cell borders. Prefer subtle horizontal separation where the table implementation supports it.
- Test with empty, typical, and large data sets. A layout that works for a few rows may fail with hundreds.
- Do not assume `journal_table.py` or `grid_table.py` behaves exactly like a standard `ttk.Treeview`; inspect the specific implementation.
- **Debit and credit lines use the same size and weight; the credit line is indented. Description lines are smaller, italic and muted.**
- **Single-row tables (Journal, Ledger): solid PRIMARY header with white bold text. The two-tier Worksheet header uses the soft PRIMARY_LIGHT style.**

### 4.6 Empty, error, and feedback states

- Empty states should explain what the user is seeing and, where useful, what action to take next.
- Validation errors should identify the field or entry that needs attention.
- Success feedback should be concise and should not interrupt routine work unnecessarily.
- Warnings and errors must remain distinguishable without depending only on color.
- Do not remove confirmation steps for destructive operations as part of visual cleanup.

---

## 5. Layout and Responsive Behavior

This is a desktop application, so layout decisions should be based on the actual window and widget behavior rather than web breakpoints.

Current main-window settings documented by the project:

- Initial size: **1280 × 760**
- Minimum size: **1000 × 600**
- Main navigation: notebook tabs for **Journal**, **Ledger**, and **Worksheet**

Layout guidance:

1. Design for the minimum supported window size as well as the initial size.
2. Keep important actions and the primary working area visible without unnecessary scrolling.
3. Align screen titles, filters, forms, and table edges to a consistent visual grid.
4. Use available horizontal space thoughtfully; do not stretch short labels or narrow controls without purpose.
5. For wide tables, preserve access to all columns through the existing horizontal-scroll behavior where supported.
6. Avoid layouts that rely on fixed pixel positions when the existing project uses Tkinter geometry managers.
7. Check the visual result at both the initial and minimum window sizes after significant layout changes.

The current Journal controls and Worksheet exports use 24 px outer spacing and 12–16 px internal gaps, as documented in the existing design. Treat these as established screen guidance, not as a rule that every screen must use identical padding.

---

## 6. Interaction and Accessibility

Visual improvements must not make the application harder to operate.

### Existing keyboard interactions

Preserve these documented shortcuts and behaviors:

| Shortcut | Existing behavior |
| --- | --- |
| `F5` | Refresh |
| `Ctrl+N` | New entry |
| `Ctrl+F` | Journal search |
| `Enter` | Submit |
| `Escape` | Dismiss |
| `Delete` | Delete selected journal entry when in the Journal tab |

The Delete behavior is specific to the Journal tab. The Edit menu no longer contains a Delete Entry action. Do not generalize this shortcut to other screens without an explicit product decision.

### Accessibility expectations

- Keep text/background contrast strong enough for comfortable reading.
- Keep keyboard navigation and visible focus feedback.
- Do not use color as the only indication of selection, validation, warning, or success.
- Use meaningful labels and clear button text.
- Preserve logical focus order.
- Do not make important information available only through hover.
- Ensure selected rows and active tabs remain visually identifiable.
- Avoid shrinking text simply to fit more information; reconsider spacing or layout first.

---

## 7. Design-Only Change Protocol

This section is mandatory guidance for AI assistants and developers making visual changes.

### Before editing

1. Read this document.
2. Inspect the target screen and its relevant source files.
3. Identify whether the component uses a shared ttk style, a custom Canvas/table implementation, or screen-specific styling.
4. Search for other screens that use the same shared style or helper.
5. State the intended visual changes and identify any possible cross-screen impact.
6. Confirm the task scope. If the request is design-only, do not alter behavior.

### During editing

- Prefer updating shared tokens or styles in `style.py` when the change is genuinely reusable.
- Prefer screen-specific changes when the design decision applies only to one screen.
- Reuse existing constants and styles instead of introducing duplicates.
- Keep changes focused; do not redesign unrelated screens.
- Preserve widget names and references, callbacks, event bindings, commands, validation, data flow, calculations, and database behavior.
- Do not change accounting rules, `Decimal` calculations, data structures, persistence, or SQL as part of a design-only task.
- Do not add a new dependency or replace a widget implementation without approval.
- If a new reusable token or component pattern is introduced, document it here and implement it in the appropriate shared source.

### After editing

1. List every modified file and explain why it changed.
2. Summarize the visual changes in plain language.
3. Identify shared styles that may affect other screens.
4. Verify the application starts and the affected screen renders.
5. Test the affected component's normal, selected/focused, disabled/error, and empty states where applicable.
6. Check the initial and minimum window sizes for layout regressions.
7. Confirm that existing commands, keyboard shortcuts, event handlers, and data behavior remain intact.
8. Report anything that could not be tested. Never claim verification that was not performed.

### Scope rule

A request to "make it look better," "modernize," or "clean up the UI" does not authorize functional changes. Ask before changing behavior, navigation, workflows, data, or accounting logic.

---

## 8. Screen-Specific Specifications

Global design rules live in this document. Screen-specific hierarchy, content priorities, states, and layout decisions belong in `.impeccable/surfaces/`.

Before redesigning a screen:

1. Read its surface specification if one exists.
2. Follow the global tokens and component rules in this document.
3. Keep screen-specific decisions consistent with the rest of the application.
4. If a screen specification conflicts with this document, identify the conflict rather than choosing silently.
5. Once a design decision is approved and reusable, update this document or the relevant surface specification.

Current known surface specification:

- `.impeccable/surfaces/ledger-tab.md` — Ledger tab design brief.

Do not assume a screen has a complete specification merely because a file exists; check its contents and unresolved decisions.

---

## 9. Change Management

Keep this document aligned with the implementation.

Update `DESIGN.md` when:

- A design token is added, removed, or changed.
- A shared component style is introduced or materially changed.
- A reusable layout or interaction pattern becomes an established standard.
- A global accessibility or interaction rule changes.

Do not update this document for every one-off padding adjustment or temporary experiment.

When documenting a new rule, distinguish between:

- **Implemented:** currently present in the code.
- **Approved guidance:** a design rule that should be followed but may not yet be implemented everywhere.
- **Proposed:** an idea that still needs review and must not be treated as an existing feature.

This distinction prevents AI assistants from confusing a desired design with a capability that already exists.

---

## 10. Quick Reference for AI Assistants

Before making a UI change, remember:

- **Read:** `DESIGN.md` and the relevant screen specification.
- **Inspect:** actual implementation in `style.py` and the target screen files.
- **Reuse:** existing tokens, styles, helpers, and semantic table tags.
- **Limit:** changes to the requested component and necessary shared styling.
- **Protect:** accounting logic, data, callbacks, keyboard behavior, and workflows.
- **Verify:** actual rendering and affected interaction states.
- **Document:** new reusable design decisions and any unresolved limitations.

**The goal is not to make every screen visually identical. The goal is to make every screen feel like it belongs to the same calm, clear, dependable accounting application.**