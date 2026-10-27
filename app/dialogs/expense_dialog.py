from datetime import date
from decimal import Decimal

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QTextEdit,
)

from app.db.models import EXPENSE_CATEGORIES
from app.widgets.date_edit import make_date_edit


class ExpenseDialog(QDialog):
    def __init__(self, parent=None, project_id: int | None = None, expense=None):
        super().__init__(parent)
        self.setWindowTitle("Expense details")
        self.setMinimumWidth(420)
        self.project_id = project_id if expense is None else expense.project_id

        layout = QFormLayout(self)
        self.title = QLineEdit()
        self.category = QComboBox()
        self.category.addItems(list(EXPENSE_CATEGORIES))
        self.amount = QDoubleSpinBox()
        self.amount.setRange(0.01, 1_000_000_000)
        self.amount.setDecimals(2)
        self.amount.setSingleStep(10)
        self.expense_date = make_date_edit()
        self.expense_date.setDate(QDate.currentDate())
        self.notes = QTextEdit()
        self.notes.setMaximumHeight(70)

        layout.addRow("Title *", self.title)
        layout.addRow("Category", self.category)
        layout.addRow("Amount *", self.amount)
        layout.addRow("Date", self.expense_date)
        layout.addRow("Notes", self.notes)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        if expense:
            self.title.setText(expense.title)
            self.category.setCurrentText(expense.category)
            self.amount.setValue(float(expense.amount))
            d = expense.expense_date
            self.expense_date.setDate(QDate(d.year, d.month, d.day))
            self.notes.setPlainText(expense.notes or "")

    def validate_and_accept(self):
        if not self.title.text().strip():
            QMessageBox.warning(self, "Validation", "Title is required.")
            return
        if self.amount.value() <= 0:
            QMessageBox.warning(self, "Validation", "Amount must be positive.")
            return
        if self.project_id is None:
            QMessageBox.warning(self, "Validation", "No project selected.")
            return
        self.accept()

    def values(self):
        qdate = self.expense_date.date()
        return {
            "project_id": self.project_id,
            "title": self.title.text().strip(),
            "category": self.category.currentText(),
            "amount": Decimal(str(self.amount.value())),
            "expense_date": date(qdate.year(), qdate.month(), qdate.day()),
            "notes": self.notes.toPlainText().strip(),
        }
