from decimal import Decimal

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.db.repository import delete_expense, list_expenses, save_expense
from app.dialogs.expense_dialog import ExpenseDialog
from app.utils import money
from app.widgets.table_page import fill_table, make_table, selected_id


class ExpensesPage(QWidget):
    def __init__(self, on_changed=None):
        super().__init__()
        self.on_changed = on_changed
        self.project_id: int | None = None
        self.setObjectName("contentArea")
        self._rows = []
        self._search_timer = QTimer(self)
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(220)
        self._search_timer.timeout.connect(self._apply_view)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 26, 28, 26)
        layout.setSpacing(14)

        top = QHBoxLayout()
        title = QLabel("Expenses")
        title.setObjectName("pageTitle")
        top.addWidget(title)
        top.addStretch()
        add = QPushButton("+ Add expense")
        add.setObjectName("primaryButton")
        add.clicked.connect(self.add_expense)
        top.addWidget(add)
        layout.addLayout(top)

        filters = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search title, category, notes, amount…")
        self.search.textChanged.connect(self._on_search_changed)
        filters.addWidget(self.search, 1)

        filters.addWidget(QLabel("Sort by"))
        self.sort_combo = QComboBox()
        for label, key in (
            ("Date · newest", "date_desc"),
            ("Date · oldest", "date_asc"),
            ("Title A–Z", "title_asc"),
            ("Title Z–A", "title_desc"),
            ("Category A–Z", "category_asc"),
            ("Amount · high–low", "amount_desc"),
            ("Amount · low–high", "amount_asc"),
        ):
            self.sort_combo.addItem(label, key)
        self.sort_combo.currentIndexChanged.connect(self._apply_view)
        filters.addWidget(self.sort_combo)
        layout.addLayout(filters)

        self.summary = QLabel("Total expenses: 0.00")
        self.summary.setObjectName("muted")
        layout.addWidget(self.summary)

        self.table = make_table(
            ["ID", "Date", "Title", "Category", "Amount", "Notes"]
        )
        layout.addWidget(self.table)

        controls = QHBoxLayout()
        edit = QPushButton("Edit")
        edit.clicked.connect(self.edit_expense)
        remove = QPushButton("Delete")
        remove.setObjectName("dangerButton")
        remove.clicked.connect(self.remove_expense)
        refresh = QPushButton("Refresh")
        refresh.clicked.connect(self.refresh)
        controls.addWidget(edit)
        controls.addWidget(remove)
        controls.addWidget(refresh)
        controls.addStretch()
        layout.addLayout(controls)

    def set_project(self, project_id: int | None):
        self.project_id = project_id
        self.refresh()

    def _notify(self):
        if self.on_changed:
            self.on_changed()

    def _on_search_changed(self, *_):
        self._search_timer.start()

    def refresh(self):
        if self.project_id is None:
            self._rows = []
            self._apply_view()
            return
        self._rows = list_expenses(self.project_id)
        self._apply_view()

    def _filtered_sorted(self) -> list:
        query = self.search.text().strip().lower()
        rows = self._rows
        if query:
            rows = [
                e
                for e in rows
                if query
                in " ".join(
                    [
                        e.title or "",
                        e.category or "",
                        e.notes or "",
                        money(e.amount),
                        e.expense_date.isoformat(),
                    ]
                ).lower()
            ]

        key = self.sort_combo.currentData() or "date_desc"
        sorters = {
            "date_desc": lambda e: (e.expense_date, e.id),
            "date_asc": lambda e: (e.expense_date, e.id),
            "title_asc": lambda e: ((e.title or "").lower(), e.id),
            "title_desc": lambda e: ((e.title or "").lower(), e.id),
            "category_asc": lambda e: ((e.category or "").lower(), e.id),
            "amount_desc": lambda e: (Decimal(str(e.amount)), e.id),
            "amount_asc": lambda e: (Decimal(str(e.amount)), e.id),
        }
        reverse = key.endswith("_desc")
        rows = sorted(rows, key=sorters.get(key, sorters["date_desc"]), reverse=reverse)
        return rows

    def _apply_view(self):
        visible = self._filtered_sorted()
        fill_table(
            self.table,
            [
                (
                    e.id,
                    e.expense_date.isoformat(),
                    e.title,
                    e.category,
                    money(e.amount),
                    e.notes or "",
                )
                for e in visible
            ],
        )
        total_all = sum((Decimal(str(e.amount)) for e in self._rows), Decimal("0"))
        total_visible = sum((Decimal(str(e.amount)) for e in visible), Decimal("0"))
        total = len(self._rows)
        shown = len(visible)
        if self.project_id is None:
            self.summary.setText("Select a project first")
        elif shown == total:
            self.summary.setText(
                f"{total} expense(s) · Total {money(total_all)}"
            )
        else:
            self.summary.setText(
                f"Showing {shown} of {total} · Filtered total {money(total_visible)} "
                f"· Full total {money(total_all)}"
            )

    def add_expense(self):
        if self.project_id is None:
            QMessageBox.information(self, "No project", "Open a project first.")
            return
        dialog = ExpenseDialog(self, project_id=self.project_id)
        if dialog.exec():
            try:
                save_expense(None, dialog.values())
                self.refresh()
                self._notify()
            except Exception as exc:
                QMessageBox.critical(self, "Save failed", str(exc))

    def edit_expense(self):
        expense_id = selected_id(self.table)
        if expense_id is None:
            QMessageBox.information(self, "Select expense", "Select an expense first.")
            return
        expense = next((e for e in self._rows if e.id == expense_id), None)
        if expense is None:
            return
        dialog = ExpenseDialog(self, project_id=self.project_id, expense=expense)
        if dialog.exec():
            try:
                save_expense(expense_id, dialog.values())
                self.refresh()
                self._notify()
            except Exception as exc:
                QMessageBox.critical(self, "Save failed", str(exc))

    def remove_expense(self):
        expense_id = selected_id(self.table)
        if expense_id is None:
            QMessageBox.information(self, "Select expense", "Select an expense first.")
            return
        if (
            QMessageBox.question(self, "Confirm deletion", "Delete this expense?")
            != QMessageBox.StandardButton.Yes
        ):
            return
        try:
            delete_expense(expense_id)
            self.refresh()
            self._notify()
        except Exception as exc:
            QMessageBox.critical(self, "Delete failed", str(exc))
