"""Saving/loading the data file and the account list."""
import json
import os
import shutil
from datetime import datetime
from decimal import Decimal, InvalidOperation
from tkinter import messagebox

from constants import CHART, DATA_FILE, ASSET, LIAB, CAP, DRAW, REV, EXP, TYPES

MAX_BACKUPS = 20


class DataMixin:
    def _validate_data(self, data):
        """Validate loaded data structure and return cleaned data."""
        if not isinstance(data, dict):
            raise ValueError("Data file must contain a JSON object")

        entries = data.get("entries", [])
        custom = data.get("custom", {})

        if not isinstance(entries, list):
            raise ValueError("'entries' must be a list")
        if not isinstance(custom, dict):
            raise ValueError("'custom' must be a dictionary")

        # Validate each entry has required fields and valid values
        valid_entries = []
        skipped = 0
        for i, entry in enumerate(entries):
            if not isinstance(entry, dict):
                skipped += 1
                continue  # Skip invalid entries

            # Check required fields exist
            required = ["date", "debit", "credit", "amount"]
            if not all(field in entry for field in required):
                skipped += 1
                continue

            # Validate date format (YYYY-MM-DD)
            try:
                datetime.strptime(entry["date"], "%Y-%m-%d")
            except (ValueError, TypeError):
                skipped += 1
                continue

            # Validate debit and credit are non-empty strings
            debit = entry["debit"]
            credit = entry["credit"]
            if not isinstance(debit, str) or not debit.strip():
                skipped += 1
                continue
            if not isinstance(credit, str) or not credit.strip():
                skipped += 1
                continue

            # Validate amount: must be valid Decimal, finite, > 0
            try:
                amt = Decimal(str(entry["amount"]))
                if not amt.is_finite() or amt <= 0:
                    raise InvalidOperation
                # Normalize to string with 2 decimal places
                entry["amount"] = str(amt.quantize(Decimal("0.01")))
            except (InvalidOperation, ValueError, TypeError):
                skipped += 1
                continue

            # Coerce adj to bool if present
            if "adj" in entry:
                entry["adj"] = bool(entry["adj"])
            else:
                entry["adj"] = False

            # Ensure optional fields exist
            entry.setdefault("desc", "")

            valid_entries.append(entry)
        # Custom accounts must have a known type; set any unknown type to Asset (the app's default)
        fixed_types = []
        for name, acct_type in custom.items():
            if acct_type not in TYPES:
                custom[name] = ASSET
                fixed_types.append(name)
        self.fixed_custom_types = fixed_types
        return valid_entries, custom, skipped

    def load(self):
        self.load_failed = False  # Reset at start
        self.load_skipped = False  # True when some entries in the file were skipped
        self.fixed_custom_types = []  # Accounts whose unknown type was set to Asset
        try:
            with open(DATA_FILE, encoding="utf-8") as f:
                d = json.load(f)
            self.entries, self.custom, skipped = self._validate_data(d)
            self.sync_custom_accounts()  # Clean up orphaned custom accounts on load
            self.load_skipped = skipped > 0
            if self.fixed_custom_types:
                messagebox.showwarning(
                    "Account Type Warning",
                    "These accounts had an unknown type and were set to Asset:\n\n"
                    + "\n".join(self.fixed_custom_types)
                    + "\n\nCheck the data file if this is wrong."
                )
            if skipped > 0:
                messagebox.showwarning(
                    "Data Load Warning",
                    f"{skipped} journal entr{'y' if skipped == 1 else 'ies'} were skipped due to invalid data.\n\n"
                    "The data file was not modified. Check the file for entries with invalid amounts, "
                    "dates, or missing accounts."
                )
            self.load_failed = False  # Success
        except FileNotFoundError:
            # File doesn't exist yet - this is fine for first run
            self.load_failed = False
            pass
        except PermissionError:
            messagebox.showerror(
                "Cannot Read Data File",
                f"Permission denied when reading {DATA_FILE}\n\n"
                "Possible causes:\n"
                "• The file is open in another program\n"
                "• You don't have permission to read this file\n\n"
                "Solution: Close other programs and restart the app."
            )
            self.entries, self.custom = [], {}
            self.load_failed = False
        except json.JSONDecodeError as err:
            # Check if there's a backup we can restore from
            backup_dir = os.path.dirname(DATA_FILE)
            backups = [f for f in os.listdir(backup_dir) if f.startswith("accounting_data.backup.")]
            backup_msg = ""
            if backups:
                backups.sort(reverse=True)
                backup_msg = (
                    f"\n\nFound {len(backups)} backup file(s).\n"
                    "You can restore from a backup by:\n"
                    "1. Closing this app\n"
                    "2. Renaming a backup file to 'accounting_data.json'\n"
                    "3. Restarting the app"
                )

            messagebox.showerror(
                "Data File is Corrupted",
                f"Cannot load accounting_data.json:\n{err}\n\n"
                "The file contains invalid JSON. This may happen if:\n"
                "• The file was edited by hand incorrectly\n"
                "• The file was corrupted during a save\n"
                "• Another program modified it"
                f"{backup_msg}"
            )
            self.entries, self.custom = [], {}
            self.load_failed = True
        except ValueError as err:
            messagebox.showerror(
                "Invalid Data Format",
                f"The data file has an invalid structure:\n{err}\n\n"
                "Some entries may have been skipped.\n"
                "The app will continue with the valid entries."
            )
            self.entries, self.custom = [], {}
            self.load_failed = True
        except Exception as err:
            messagebox.showerror(
                "Unexpected Error",
                f"An unexpected error occurred while loading data:\n{err}\n\n"
                "The app will start with empty data. Your previous data may still be "
                "recoverable from a backup file."
            )
            self.entries, self.custom = [], {}
            self.load_failed = True

    def _create_backup(self, new_content: bytes = None):
        """Create a timestamped backup of the data file before saving.

        If new_content is provided, compares against that instead of the current file.
        This allows skipping backups when the new content would be identical to the newest backup.
        """
        if not os.path.exists(DATA_FILE):
            return

        # If load failed, copy the bad file to unreadable.* and don't create a normal backup
        if getattr(self, 'load_failed', False):
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")
            backup_dir = os.path.dirname(DATA_FILE)
            backup_name = f"accounting_data.unreadable.{timestamp}.json"
            backup_path = os.path.join(backup_dir, backup_name)
            try:
                shutil.copy2(DATA_FILE, backup_path)
                self.load_failed = False  # Only copy once
            except OSError:
                pass  # Backup failed, but continue with save
            return

        # Normal backup: check if content is same as newest backup
        backup_dir = os.path.dirname(DATA_FILE)
        backups = [f for f in os.listdir(backup_dir) if f.startswith("accounting_data.backup.")]
        if backups:
            backups.sort(reverse=True)  # Newest first
            newest_backup = os.path.join(backup_dir, backups[0])
            try:
                # Compare against new_content if provided, otherwise current file
                # Normalize line endings for comparison (Windows vs Unix)
                if new_content is not None:
                    with open(newest_backup, 'rb') as f2:
                        backup_content = f2.read()
                        # Normalize both to \n for comparison
                        if new_content.replace(b'\r\n', b'\n') == backup_content.replace(b'\r\n', b'\n'):
                            return  # Same content, skip backup
                else:
                    with open(DATA_FILE, 'rb') as f1, open(newest_backup, 'rb') as f2:
                        if f1.read() == f2.read():
                            return  # Same content, skip backup
            except OSError:
                pass  # If comparison fails, proceed with backup

        # Create unique backup name with microsecond resolution
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")
        backup_name = f"accounting_data.backup.{timestamp}.json"
        backup_path = os.path.join(backup_dir, backup_name)

        # If name already exists (extremely unlikely), add counter
        counter = 1
        while os.path.exists(backup_path):
            backup_name = f"accounting_data.backup.{timestamp}_{counter}.json"
            backup_path = os.path.join(backup_dir, backup_name)
            counter += 1

        try:
            # Write new_content if provided (so backup matches new format), else copy file
            if new_content is not None:
                with open(backup_path, 'wb') as f:
                    f.write(new_content)
            else:
                shutil.copy2(DATA_FILE, backup_path)
            self._cleanup_old_backups()
        except OSError:
            pass  # Backup failed, but continue with save

    def _cleanup_old_backups(self):
        """Keep only the MAX_BACKUPS most recent backup files."""
        backup_dir = os.path.dirname(DATA_FILE)
        backups = [f for f in os.listdir(backup_dir) if f.startswith("accounting_data.backup.")]
        backups.sort(reverse=True)  # Newest first

        for old_backup in backups[MAX_BACKUPS:]:
            try:
                os.remove(os.path.join(backup_dir, old_backup))
            except OSError:
                pass

    def save(self):
        """Save the data file. Return True if saved, False if the save failed (a dialog was already shown)."""
        temp_path = DATA_FILE + ".tmp"
        try:
            # Build JSON text first (if dumps fails, nothing on disk is touched)
            text = json.dumps({"entries": self.entries, "custom": self.custom}, indent=2)
            # If the file had skipped entries, keep a copy of the ORIGINAL file before
            # this save overwrites it. If the copy fails, the OSError below stops the save.
            if getattr(self, "load_skipped", False) and os.path.exists(DATA_FILE):
                stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")
                skipped_path = os.path.join(os.path.dirname(DATA_FILE),
                                            f"accounting_data.skipped.{stamp}.json")
                shutil.copy2(DATA_FILE, skipped_path)
                self.load_skipped = False  # Only keep one copy per load
            # Create backup, comparing against the new content we're about to write
            self._create_backup(text.encode('utf-8'))
            # Write to temp file in the same folder
            with open(temp_path, "w", encoding="utf-8") as f:
                f.write(text)
                f.flush()
                os.fsync(f.fileno())
            # Atomic replace: DATA_FILE is always either complete old or complete new
            os.replace(temp_path, DATA_FILE)
            return True
        except PermissionError:
            # Clean up temp file if it exists
            try:
                os.remove(temp_path)
            except OSError:
                pass
            messagebox.showerror(
                "Save Failed - Permission Denied",
                f"Cannot save to {DATA_FILE}\n\n"
                "Possible causes:\n"
                "• The file is open in another program (Excel, Notepad, etc.)\n"
                "• You don't have write permission to this folder\n\n"
                "Solution: Close any programs that might be using this file and try again."
            )
            return False
        except OSError as err:
            # Clean up temp file if it exists
            try:
                os.remove(temp_path)
            except OSError:
                pass
            error_msg = str(err).lower()
            if "no space" in error_msg or "disk full" in error_msg:
                messagebox.showerror(
                    "Save Failed - Disk Full",
                    "Cannot save: Your disk is full.\n\n"
                    "Solution: Free up disk space and try again."
                )
            elif "read-only" in error_msg:
                messagebox.showerror(
                    "Save Failed - Read-Only File",
                    f"Cannot save: {DATA_FILE} is read-only.\n\n"
                    "Solution: Right-click the file → Properties → uncheck 'Read-only'"
                )
            else:
                messagebox.showerror(
                    "Save Failed",
                    f"Cannot save accounting data:\n{err}\n\n"
                    "If the problem persists, check file permissions and available disk space."
                )
            return False
        except Exception as err:
            # Clean up temp file if it exists
            try:
                os.remove(temp_path)
            except OSError:
                pass
            messagebox.showerror(
                "Unexpected Error",
                f"An unexpected error occurred while saving:\n{err}\n\n"
                "Your data may not have been saved. Please try again."
            )
            return False

    def all_account_names(self):
        """Return account names for dropdown: CHART first, then explicitly added custom accounts.
        Does NOT include accounts only referenced in entries (use get_all_account_names for that)."""
        return [n for n, _ in CHART] + list(self.custom)

    def get_all_account_names(self):
        """Return ALL account names for worksheet computation: CHART + explicit custom + entry-referenced."""
        chart = [n for n, _ in CHART]
        explicit_custom = list(self.custom)
        # Add accounts referenced in entries but not in chart or explicit custom
        referenced = set()
        for e in self.entries:
            referenced.add(e["debit"])
            referenced.add(e["credit"])
        extra = [n for n in referenced if n not in chart and n not in explicit_custom]
        names = chart + explicit_custom + extra
        t = self.types()
        order = [ASSET, LIAB, CAP, DRAW, REV, EXP]
        return sorted(names, key=lambda n: order.index(t[n]))

    def types(self):
        t = dict(CHART)
        t.update(self.custom)
        # Add types for entry-referenced accounts (default to Asset if unknown)
        for e in self.entries:
            if e["debit"] not in t:
                t[e["debit"]] = ASSET
            if e["credit"] not in t:
                t[e["credit"]] = ASSET
        return t

    def add_custom_account(self, name, account_type):
        """Add a custom account to the chart (appears in dropdown)."""
        self.custom[name] = account_type

    def sync_custom_accounts(self):
        """Keep referenced custom accounts and recover legacy accounts as Assets."""
        referenced = set()
        for e in self.entries:
            referenced.add(e["debit"])
            referenced.add(e["credit"])
        chart_names = {n for n, _ in CHART}
        for name in referenced:
            if name not in chart_names:
                self.custom.setdefault(name, ASSET)
        self.custom = {k: v for k, v in self.custom.items() if k in referenced or k in chart_names}