#!/usr/bin/env python3
"""
CLI Expense Tracker
- Stores expenses in a CSV file (expenses.csv)
- Supports: add, list, summary by category, export, quit
"""

import csv
import os
from datetime import datetime
from collections import defaultdict, OrderedDict

CSV_FILE = "expenses.csv"
CSV_HEADERS = ["id", "date", "name", "amount", "category", "notes"]


class Expense:
    def __init__(self, id_, date, name, amount, category, notes=""):
        self.id = id_
        self.date = date  # string YYYY-MM-DD
        self.name = name
        self.amount = float(amount)
        self.category = category
        self.notes = notes

    def to_row(self):
        return [self.id, self.date, self.name, f"{self.amount:.2f}", self.category, self.notes]

    @staticmethod
    def from_row(row):
        return Expense(row[0], row[1], row[2], row[3], row[4], row[5] if len(row) > 5 else "")


class ExpenseTracker:
    def __init__(self, csv_file=CSV_FILE):
        self.csv_file = csv_file
        self.expenses = OrderedDict()  # id -> Expense
        self._load()

    def _load(self):
        if not os.path.exists(self.csv_file):
            # create file with header
            with open(self.csv_file, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(CSV_HEADERS)
            return
        with open(self.csv_file, newline="") as f:
            reader = csv.reader(f)
            headers = next(reader, None)
            for row in reader:
                if not row:
                    continue
                e = Expense.from_row(row)
                self.expenses[e.id] = e

    def _save(self):
        with open(self.csv_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADERS)
            for e in self.expenses.values():
                writer.writerow(e.to_row())

    def _next_id(self):
        if not self.expenses:
            return "1"
        return str(int(next(reversed(self.expenses))) + 1)

    def add_expense(self, name, amount, category, date=None, notes=""):
        if date is None or date.strip() == "":
            date = datetime.today().strftime("%Y-%m-%d")
        id_ = self._next_id()
        e = Expense(id_, date, name, amount, category, notes)
        self.expenses[id_] = e
        self._save()
        return e

    def list_expenses(self, limit=None):
        items = list(self.expenses.values())
        if limit:
            items = items[-limit:]
        return items

    def total_spent(self):
        return sum(e.amount for e in self.expenses.values())

    def summary_by_category(self):
        agg = defaultdict(float)
        for e in self.expenses.values():
            agg[e.category] += e.amount
        return dict(agg)

    def summary_by_month(self):
        agg = defaultdict(float)
        for e in self.expenses.values():
            month = e.date[:7]  # YYYY-MM
            agg[month] += e.amount
        return dict(agg)

    def export_csv(self, target_file):
        with open(target_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADERS)
            for e in self.expenses.values():
                writer.writerow(e.to_row())
        return target_file


def print_expense(e: Expense):
    print(f"[{e.id}] {e.date} | {e.name} | ₹{e.amount:.2f} | {e.category} | {e.notes}")


def main():
    print("=== CLI Expense Tracker ===")
    tracker = ExpenseTracker()

    while True:
        print("\nChoose an option:")
        print("1. Add expense")
        print("2. List expenses")
        print("3. Show total spent")
        print("4. Summary by category")
        print("5. Summary by month")
        print("6. Export CSV")
        print("7. Quit")

        choice = input("Enter choice (1-7): ").strip()

        if choice == "1":
            name = input("Expense name: ").strip()
            amount = input("Amount (numeric): ").strip()
            category = input("Category (e.g., Food, Travel, Bills): ").strip() or "General"
            date = input("Date (YYYY-MM-DD) [press enter for today]: ").strip()
            notes = input("Notes (optional): ").strip()
            try:
                e = tracker.add_expense(name, float(amount), category, date if date else None, notes)
                print("Added:")
                print_expense(e)
            except ValueError:
                print("Invalid amount. Please enter a number like 150.50")

        elif choice == "2":
            limit = input("Show last N entries (press enter for all): ").strip()
            limit_val = int(limit) if limit.isdigit() else None
            items = tracker.list_expenses(limit_val)
            if not items:
                print("No expenses recorded yet.")
            for e in items:
                print_expense(e)

        elif choice == "3":
            total = tracker.total_spent()
            print(f"Total spent: ₹{total:.2f}")

        elif choice == "4":
            summary = tracker.summary_by_category()
            if not summary:
                print("No records yet.")
            else:
                print("Spending by category:")
                for cat, amt in sorted(summary.items(), key=lambda x: -x[1]):
                    print(f" - {cat}: ₹{amt:.2f}")

        elif choice == "5":
            summary = tracker.summary_by_month()
            if not summary:
                print("No records yet.")
            else:
                print("Spending by month:")
                for month, amt in sorted(summary.items()):
                    print(f" - {month}: ₹{amt:.2f}")

        elif choice == "6":
            target = input("Export filename [default: export.csv]: ").strip() or "export.csv"
            tracker.export_csv(target)
            print(f"Exported to {target}")

        elif choice == "7":
            print("Goodbye — your data is saved in", tracker.csv_file)
            break
        else:
            print("Invalid choice. Enter 1-7.")


if __name__ == "__main__":
    main()
