from datetime import date
from decimal import Decimal

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QWidget,
)

from app.auth.session import current_session
from app.db.models import PAYMENT_METHODS, compute_donation_status
from app.db.repository import list_collector_choices
from app.utils import money
from app.widgets.date_edit import make_date_edit

REFERENCE_HELP = (
    "Optional payment tracking ID — for example a bank transfer number, "
    "cheque number, mobile-money transaction ID, or receipt/voucher code. "
    "It does not affect totals or status; leave blank if unused."
)


def _label_with_info(text: str, tip: str) -> QWidget:
    row = QWidget()
    layout = QHBoxLayout(row)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(6)
    layout.addWidget(QLabel(text))
    info = QPushButton("i")
    info.setObjectName("infoIconButton")
    info.setFixedSize(20, 20)
    info.setCursor(Qt.CursorShape.WhatsThisCursor)
    info.setToolTip(tip)
    info.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    info.clicked.connect(lambda: QMessageBox.information(info.window(), text, tip))
    layout.addWidget(info)
    layout.addStretch()
    return row


class DonationDialog(QDialog):
    def __init__(
        self,
        parent=None,
        donors=None,
        project_id: int | None = None,
        donation=None,
        *,
        focus_payment: bool = False,
    ):
        super().__init__(parent)
        self.setWindowTitle(
            "Record payment" if focus_payment and donation else "Donation details"
        )
        self.setMinimumWidth(480)
        donors = donors or []
        self.project_id = project_id if donation is None else donation.project_id
        self._donation_id = donation.id if donation is not None else None
        self._locked_donor_id = donation.donor_id if donation is not None else None
        self._original_paid = (
            Decimal(str(donation.paid_amount)) if donation is not None else Decimal("0")
        )

        layout = QFormLayout(self)
        self.donor = QComboBox()
        self.donor.setEditable(True)
        self.donor.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.donor.lineEdit().setPlaceholderText("Search donor by name…")
        for item in donors:
            label = item.name
            if item.email:
                label = f"{item.name}  ({item.email})"
            self.donor.addItem(label, item.id)
        self.donor.setCurrentIndex(-1 if donation is None else 0)

        self.pledged = QDoubleSpinBox()
        self.pledged.setRange(0.01, 1_000_000_000)
        self.pledged.setDecimals(2)
        self.pledged.setSingleStep(10)

        self.paid = QDoubleSpinBox()
        self.paid.setRange(0, 1_000_000_000)
        self.paid.setDecimals(2)
        self.paid.setSingleStep(10)

        self.add_payment = QDoubleSpinBox()
        self.add_payment.setRange(0, 1_000_000_000)
        self.add_payment.setDecimals(2)
        self.add_payment.setSingleStep(10)
        self.add_payment.setToolTip(
            "Amount received now — added on top of what is already paid."
        )

        self.remaining_label = QLabel("0.00")
        self.remaining_label.setObjectName("muted")

        self.status_label = QLabel("Pending")
        self.status_label.setObjectName("badge")

        self.donation_date = make_date_edit()
        self.donation_date.setDate(QDate.currentDate())

        self.payment_method = QComboBox()
        self.payment_method.addItems(list(PAYMENT_METHODS))

        self.collected_by = QComboBox()
        self.collected_by.setEditable(True)
        self.collected_by.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.collected_by.lineEdit().setPlaceholderText("Search staff who collected…")
        self._collectors = list_collector_choices()
        for user in self._collectors:
            label = user.display_name
            if user.username and user.username.lower() != label.lower():
                label = f"{label}  (@{user.username})"
            self.collected_by.addItem(label, user.id)
        self.collected_by.setCurrentIndex(-1)

        self.reference = QLineEdit()
        self.reference.setPlaceholderText("e.g. bank slip / cheque / M-Pesa ID")
        self.reference.setToolTip(REFERENCE_HELP)
        self.notes = QTextEdit()
        self.notes.setMaximumHeight(70)

        layout.addRow("Donor *", self.donor)
        layout.addRow("Raised / pledged *", self.pledged)

        self._paid_label = "Paid amount" if donation is None else "Already paid"
        layout.addRow(self._paid_label, self.paid)

        self.pay_row = QWidget()
        pay_layout = QHBoxLayout(self.pay_row)
        pay_layout.setContentsMargins(0, 0, 0, 0)
        pay_layout.setSpacing(8)
        pay_layout.addWidget(self.add_payment, 1)
        self.pay_remaining_btn = QPushButton("Pay remaining")
        self.pay_remaining_btn.setObjectName("primaryButton")
        self.pay_remaining_btn.setToolTip("Set this payment to the outstanding balance.")
        self.pay_remaining_btn.clicked.connect(self._pay_remaining)
        pay_layout.addWidget(self.pay_remaining_btn)
        self._pay_row_label = QLabel("This payment")
        layout.addRow(self._pay_row_label, self.pay_row)

        layout.addRow("Still outstanding", self.remaining_label)
        layout.addRow("Status after save", self.status_label)
        layout.addRow("Payment method", self.payment_method)
        layout.addRow("Collected by *", self.collected_by)
        layout.addRow("Date", self.donation_date)
        layout.addRow(_label_with_info("Reference", REFERENCE_HELP), self.reference)
        layout.addRow("Notes", self.notes)

        self.pledged.valueChanged.connect(self._on_amounts_changed)
        self.paid.valueChanged.connect(self._on_amounts_changed)
        self.add_payment.valueChanged.connect(self._refresh_status)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        if donation:
            index = self.donor.findData(donation.donor_id)
            if index >= 0:
                self.donor.setCurrentIndex(index)
            else:
                # Donor missing from list — keep locked id and show name if known.
                name = donation.donor.name if donation.donor else f"Donor #{donation.donor_id}"
                self.donor.clear()
                self.donor.addItem(name, donation.donor_id)
                self.donor.setCurrentIndex(0)
            self.donor.setEnabled(False)
            self.pledged.setValue(float(donation.pledged_amount))
            self.paid.setValue(float(donation.paid_amount))
            # Keep "already paid" as the baseline; user enters this payment.
            self.paid.setReadOnly(True)
            self.paid.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)
            remaining = max(
                Decimal("0"),
                Decimal(str(donation.pledged_amount)) - Decimal(str(donation.paid_amount)),
            )
            self.add_payment.setValue(float(remaining) if focus_payment else 0.0)
            d = donation.donation_date
            self.donation_date.setDate(QDate(d.year, d.month, d.day))
            self.payment_method.setCurrentText(donation.payment_method)
            collector_id = getattr(donation, "collected_by_user_id", None)
            self._select_collector(collector_id)
            self.reference.setText(donation.reference or "")
            self.notes.setPlainText(donation.notes or "")
            if focus_payment:
                self.add_payment.setFocus()
                self.add_payment.selectAll()
        else:
            self.pay_row.hide()
            self._pay_row_label.hide()
            self.add_payment.setValue(0.0)
            if donors:
                self.donor.setCurrentIndex(0)
            self._select_collector(current_session.user_id)

        self._editing = donation is not None
        self._on_amounts_changed()

    def _select_collector(self, user_id: int | None):
        if user_id is None:
            user_id = current_session.user_id
        if user_id is None:
            if self.collected_by.count():
                self.collected_by.setCurrentIndex(0)
            return
        index = self.collected_by.findData(int(user_id))
        if index >= 0:
            self.collected_by.setCurrentIndex(index)
            return
        # Inactive / missing user — keep id so edits don't wipe it.
        label = f"User #{user_id}"
        for user in self._collectors:
            if user.id == int(user_id):
                label = user.display_name
                break
        self.collected_by.addItem(label, int(user_id))
        self.collected_by.setCurrentIndex(self.collected_by.count() - 1)

    def _remaining_before_payment(self) -> Decimal:
        pledged = Decimal(str(self.pledged.value()))
        paid = Decimal(str(self.paid.value()))
        rem = pledged - paid
        return rem if rem > 0 else Decimal("0")

    def _total_paid_after(self) -> Decimal:
        base = Decimal(str(self.paid.value()))
        if getattr(self, "_editing", False):
            return base + Decimal(str(self.add_payment.value()))
        return base

    def _pay_remaining(self):
        rem = self._remaining_before_payment()
        self.add_payment.setValue(float(rem))
        self._refresh_status()

    def _on_amounts_changed(self):
        rem = self._remaining_before_payment()
        self.add_payment.setMaximum(float(rem) if rem > 0 else 0.0)
        if self.add_payment.value() > float(rem):
            self.add_payment.setValue(float(rem))
        self.pay_remaining_btn.setEnabled(rem > 0)
        self._refresh_status()

    def _refresh_status(self):
        pledged = Decimal(str(self.pledged.value()))
        paid_after = self._total_paid_after()
        remaining_after = pledged - paid_after
        if remaining_after < 0:
            remaining_after = Decimal("0")
        self.remaining_label.setText(money(remaining_after))
        self.status_label.setText(compute_donation_status(pledged, paid_after))

    def validate_and_accept(self):
        donor_id = self._locked_donor_id
        if donor_id is None:
            donor_id = self.donor.currentData()
        if donor_id is None:
            QMessageBox.warning(self, "Validation", "Select a donor from the list.")
            return
        if self.pledged.value() <= 0:
            QMessageBox.warning(self, "Validation", "Pledged amount must be positive.")
            return
        paid_after = self._total_paid_after()
        if paid_after > Decimal(str(self.pledged.value())):
            QMessageBox.warning(
                self, "Validation", "Total paid cannot exceed pledged amount."
            )
            return
        if self.project_id is None:
            QMessageBox.warning(self, "Validation", "No project selected.")
            return
        if self.collected_by.currentData() is None:
            QMessageBox.warning(
                self, "Validation", "Select who collected this donation."
            )
            return
        self._locked_donor_id = int(donor_id)
        self.accept()

    def values(self):
        qdate = self.donation_date.date()
        pledged = Decimal(str(self.pledged.value()))
        paid = self._total_paid_after()
        donor_id = self._locked_donor_id
        if donor_id is None:
            donor_id = self.donor.currentData()
        return {
            "donor_id": int(donor_id),
            "project_id": self.project_id,
            "pledged_amount": pledged,
            "paid_amount": paid,
            "status": compute_donation_status(pledged, paid),
            "donation_date": date(qdate.year(), qdate.month(), qdate.day()),
            "payment_method": self.payment_method.currentText(),
            "collected_by_user_id": int(self.collected_by.currentData()),
            "reference": self.reference.text().strip(),
            "notes": self.notes.toPlainText().strip(),
        }
