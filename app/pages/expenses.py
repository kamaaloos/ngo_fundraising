from decimal import Decimal

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
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
from app.i18n import tr
from app.io.importers import import_expenses_from_file
from app.samples import customer_samples_dir, open_sample_templates
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
        title = QLabel(tr("expenses.title"))
        title.setObjectName("pageTitle")
        top.addWidget(title)
        top.addStretch()
        self.import_btn = QPushButton(tr("expenses.import"))
        self.import_btn.setObjectName("ghostButton")
        self.import_btn.clicked.connect(self.import_expenses)
        self.samples_btn = QPushButton(tr("samples.open"))
        self.samples_btn.setObjectName("ghostButton")
        self.samples_btn.clicked.connect(lambda: open_sample_templates(self))
        add = QPushButton(tr("expenses.add"))
        add.setObjectName("primaryButton")
        add.clicked.connect(self.add_expense)
        top.addWidget(self.import_btn)
        top.addWidget(self.samples_btn)
        top.addWidget(add)
        layout.addLayout(top)

        filters = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText(tr("expenses.search_ph"))
        self.search.textChanged.connect(self._on_search_changed)
        filters.addWidget(self.search, 1)

        filters.addWidget(QLabel(tr("expenses.sort_by")))
        self.sort_combo = QComboBox()
        for key, sort_key in (
            ("expenses.sort.date_desc", "date_desc"),
            ("expenses.sort.date_asc", "date_asc"),
            ("expenses.sort.title_asc", "title_asc"),
            ("expenses.sort.title_desc", "title_desc"),
            ("expenses.sort.category_asc", "category_asc"),
            ("expenses.sort.amount_desc", "amount_desc"),
            ("expenses.sort.amount_asc", "amount_asc"),
        ):
            self.sort_combo.addItem(tr(key), sort_key)
        self.sort_combo.currentIndexChanged.connect(self._apply_view)
        filters.addWidget(self.sort_combo)
        layout.addLayout(filters)

        self.summary = QLabel("")
        self.summary.setObjectName("muted")
        layout.addWidget(self.summary)

        self.table = make_table(
            [
                tr("col.id"),
                tr("col.date"),
                tr("col.title"),
                tr("col.category"),
                tr("col.amount"),
                tr("col.notes"),
            ]
        )
        layout.addWidget(self.table)

        controls = QHBoxLayout()
        edit = QPushButton(tr("common.edit"))
        edit.clicked.connect(self.edit_expense)
        remove = QPushButton(tr("common.delete"))
        remove.setObjectName("dangerButton")
        remove.clicked.connect(self.remove_expense)
        refresh = QPushButton(tr("common.refresh"))
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
            self.summary.setText(tr("common.no_project_body"))
        elif shown == total:
            self.summary.setText(
                tr("expenses.summary", count=total, total=money(total_all))
            )
        else:
            self.summary.setText(
                tr(
                    "expenses.summary_filtered",
                    shown=shown,
                    total=total,
                    filtered=money(total_visible),
                    full=money(total_all),
                )
            )

    def import_expenses(self):
        if self.project_id is None:
            QMessageBox.information(
                self, tr("common.no_project_title"), tr("common.no_project_body")
            )
            return
        start = str(customer_samples_dir()) if customer_samples_dir().exists() else ""
        path, _ = QFileDialog.getOpenFileName(
            self,
            tr("expenses.import"),
            start,
            "Spreadsheets (*.csv *.xlsx);;CSV (*.csv);;Excel (*.xlsx)",
        )
        if not path:
            return
        try:
            created, warnings = import_expenses_from_file(path, self.project_id)
        except Exception as exc:
            QMessageBox.critical(self, tr("expenses.import_failed"), str(exc))
            return
        body = tr("expenses.imported_count", count=created)
        if warnings:
            body += "\n\n" + "\n".join(warnings[:12])
            if len(warnings) > 12:
                body += f"\n… (+{len(warnings) - 12})"
        QMessageBox.information(self, tr("expenses.import_complete"), body)
        self.refresh()
        self._notify()

    def add_expense(self):
        if self.project_id is None:
            QMessageBox.information(
                self, tr("common.no_project_title"), tr("common.no_project_body")
            )
            return
        dialog = ExpenseDialog(self, project_id=self.project_id)
        if dialog.exec():
            try:
                save_expense(None, dialog.values())
                self.refresh()
                self._notify()
            except Exception as exc:
                QMessageBox.critical(self, tr("common.save_failed"), str(exc))

    def edit_expense(self):
        expense_id = selected_id(self.table)
        if expense_id is None:
            QMessageBox.information(
                self, tr("expenses.select_title"), tr("expenses.select_body")
            )
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
                QMessageBox.critical(self, tr("common.save_failed"), str(exc))

    def remove_expense(self):
        expense_id = selected_id(self.table)
        if expense_id is None:
            QMessageBox.information(
                self, tr("expenses.select_title"), tr("expenses.select_body")
            )
            return
        if (
            QMessageBox.question(
                self, tr("common.confirm_delete"), tr("expenses.confirm_body")
            )
            != QMessageBox.StandardButton.Yes
        ):
            return
        try:
            delete_expense(expense_id)
            self.refresh()
            self._notify()
        except Exception as exc:
            QMessageBox.critical(self, tr("common.delete_failed"), str(exc))
