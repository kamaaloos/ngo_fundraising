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

from app.db.repository import (
    delete_donation,
    list_all_donors,
    list_collector_choices,
    list_donations,
    save_donation,
)
from app.dialogs.collector_donations_dialog import CollectorDonationsDialog
from app.dialogs.donation_dialog import DonationDialog
from app.utils import money
from app.widgets.table_page import fill_table, make_table, selected_id


class DonationsPage(QWidget):
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
        title = QLabel("Donations")
        title.setObjectName("pageTitle")
        top.addWidget(title)
        top.addStretch()
        add = QPushButton("+ Record donation")
        add.setObjectName("primaryButton")
        add.clicked.connect(self.add_donation)
        top.addWidget(add)
        layout.addLayout(top)

        note = QLabel(
            "Any registered donor can donate to this project. "
            "Record who collected each gift, then search by collector. "
            "Flow: pledged → collected by → payment → status."
        )
        note.setObjectName("muted")
        note.setWordWrap(True)
        layout.addWidget(note)

        filters = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText(
            "Search donor, collector, status, method, reference, notes…"
        )
        self.search.textChanged.connect(self._on_search_changed)
        filters.addWidget(self.search, 1)

        filters.addWidget(QLabel("Collected by"))
        self.collector_filter = QComboBox()
        self.collector_filter.addItem("All collectors", None)
        for user in list_collector_choices():
            label = user.display_name
            if user.username and user.username.lower() != label.lower():
                label = f"{label} (@{user.username})"
            self.collector_filter.addItem(label, user.id)
        self.collector_filter.currentIndexChanged.connect(self._apply_view)
        filters.addWidget(self.collector_filter)

        filters.addWidget(QLabel("Sort by"))
        self.sort_combo = QComboBox()
        for label, key in (
            ("Date · newest", "date_desc"),
            ("Date · oldest", "date_asc"),
            ("Donor A–Z", "donor_asc"),
            ("Donor Z–A", "donor_desc"),
            ("Collector A–Z", "collector_asc"),
            ("Pledged · high–low", "pledged_desc"),
            ("Pledged · low–high", "pledged_asc"),
            ("Paid · high–low", "paid_desc"),
            ("Paid · low–high", "paid_asc"),
            ("Remaining · high–low", "remaining_desc"),
            ("Status", "status_asc"),
            ("Method", "method_asc"),
        ):
            self.sort_combo.addItem(label, key)
        self.sort_combo.currentIndexChanged.connect(self._apply_view)
        filters.addWidget(self.sort_combo)
        layout.addLayout(filters)

        self.result_label = QLabel("")
        self.result_label.setObjectName("muted")
        layout.addWidget(self.result_label)

        self.table = make_table(
            [
                "ID",
                "Date",
                "Donor",
                "Collected by",
                "Pledged",
                "Paid",
                "Remaining",
                "Method",
                "Status",
                "Reference",
            ]
        )
        layout.addWidget(self.table)

        controls = QHBoxLayout()
        pay = QPushButton("Record payment")
        pay.setObjectName("primaryButton")
        pay.setToolTip("Apply a payment toward the outstanding pledged balance.")
        pay.clicked.connect(self.record_payment)
        history = QPushButton("Payment history")
        history.setObjectName("ghostButton")
        history.setToolTip("See each installment: date, method, received by…")
        history.clicked.connect(self.view_payment_history)
        by_collector = QPushButton("By collector…")
        by_collector.setObjectName("ghostButton")
        by_collector.setToolTip(
            "Search a staff user and see every donation they collected."
        )
        by_collector.clicked.connect(self.view_by_collector)
        edit = QPushButton("Edit")
        edit.clicked.connect(self.edit_donation)
        remove = QPushButton("Delete")
        remove.setObjectName("dangerButton")
        remove.clicked.connect(self.remove_donation)
        refresh = QPushButton("Refresh")
        refresh.clicked.connect(self.refresh)
        controls.addWidget(pay)
        controls.addWidget(history)
        controls.addWidget(by_collector)
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

    def _reload_collector_filter(self):
        current = self.collector_filter.currentData()
        self.collector_filter.blockSignals(True)
        self.collector_filter.clear()
        self.collector_filter.addItem("All collectors", None)
        for user in list_collector_choices():
            label = user.display_name
            if user.username and user.username.lower() != label.lower():
                label = f"{label} (@{user.username})"
            self.collector_filter.addItem(label, user.id)
        index = self.collector_filter.findData(current)
        self.collector_filter.setCurrentIndex(index if index >= 0 else 0)
        self.collector_filter.blockSignals(False)

    def refresh(self):
        self._reload_collector_filter()
        if self.project_id is None:
            self._rows = []
            self._apply_view()
            return
        self._rows = list_donations(self.project_id)
        self._apply_view()

    def _collector_name(self, donation) -> str:
        return donation.collector_label or ""

    def _filtered_sorted(self) -> list:
        query = self.search.text().strip().lower()
        collector_id = self.collector_filter.currentData()
        rows = self._rows
        if collector_id is not None:
            rows = [
                d
                for d in rows
                if getattr(d, "collected_by_user_id", None) == collector_id
            ]
        if query:
            rows = [
                d
                for d in rows
                if query
                in " ".join(
                    [
                        d.donor.name if d.donor else "",
                        self._collector_name(d),
                        getattr(d.collected_by, "username", "") or "",
                        d.payment_method or "",
                        d.status or "",
                        d.reference or "",
                        d.notes or "",
                        money(d.pledged_amount),
                        money(d.paid_amount),
                        d.donation_date.isoformat(),
                    ]
                ).lower()
            ]

        key = self.sort_combo.currentData() or "date_desc"

        def donor_name(d):
            return (d.donor.name if d.donor else "").lower()

        sorters = {
            "date_desc": lambda d: (d.donation_date, d.id),
            "date_asc": lambda d: (d.donation_date, d.id),
            "donor_asc": lambda d: (donor_name(d), d.id),
            "donor_desc": lambda d: (donor_name(d), d.id),
            "collector_asc": lambda d: (self._collector_name(d).lower(), d.id),
            "pledged_desc": lambda d: (Decimal(str(d.pledged_amount)), d.id),
            "pledged_asc": lambda d: (Decimal(str(d.pledged_amount)), d.id),
            "paid_desc": lambda d: (Decimal(str(d.paid_amount)), d.id),
            "paid_asc": lambda d: (Decimal(str(d.paid_amount)), d.id),
            "remaining_desc": lambda d: (d.remaining_amount, d.id),
            "status_asc": lambda d: (d.status or "", d.id),
            "method_asc": lambda d: (d.payment_method or "", d.id),
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
                    d.id,
                    d.donation_date.isoformat(),
                    d.donor.name if d.donor else "",
                    self._collector_name(d) or "—",
                    money(d.pledged_amount),
                    money(d.paid_amount),
                    money(d.remaining_amount),
                    d.payment_method,
                    d.status,
                    d.reference or "",
                )
                for d in visible
            ],
        )
        total = len(self._rows)
        shown = len(visible)
        if self.project_id is None:
            self.result_label.setText("Select a project first")
        elif shown == total:
            self.result_label.setText(f"{total} donation(s)")
        else:
            self.result_label.setText(f"Showing {shown} of {total} donation(s)")

    def add_donation(self):
        if self.project_id is None:
            QMessageBox.information(self, "No project", "Open a project first.")
            return
        donors = list_all_donors()
        if not donors:
            QMessageBox.information(
                self,
                "Setup required",
                "Add at least one donor first (Donors → Add donor).",
            )
            return
        dialog = DonationDialog(self, donors=donors, project_id=self.project_id)
        if dialog.exec():
            try:
                save_donation(None, dialog.values())
                self.refresh()
                self._notify()
            except Exception as exc:
                QMessageBox.critical(self, "Save failed", str(exc))

    def _selected_donation(self):
        donation_id = selected_id(self.table)
        if donation_id is None:
            return None
        return next((d for d in self._rows if d.id == donation_id), None)

    def view_payment_history(self):
        from app.dialogs.payment_history_dialog import PaymentHistoryDialog

        donation = self._selected_donation()
        if donation is None:
            QMessageBox.information(self, "Select donation", "Select a donation first.")
            return
        PaymentHistoryDialog(self, donation_id=donation.id).exec()

    def view_by_collector(self):
        CollectorDonationsDialog(self, project_id=self.project_id).exec()

    def record_payment(self):
        donation = self._selected_donation()
        if donation is None:
            QMessageBox.information(self, "Select donation", "Select a donation first.")
            return
        remaining = donation.remaining_amount
        if remaining <= 0:
            QMessageBox.information(
                self,
                "Nothing outstanding",
                "This donation is already fully paid.",
            )
            return
        donors = list_all_donors()
        dialog = DonationDialog(
            self,
            donors=donors,
            project_id=self.project_id,
            donation=donation,
            focus_payment=True,
        )
        if dialog.exec():
            try:
                save_donation(donation.id, dialog.values())
                self.refresh()
                self._notify()
            except Exception as exc:
                QMessageBox.critical(self, "Save failed", str(exc))

    def edit_donation(self):
        donation = self._selected_donation()
        if donation is None:
            QMessageBox.information(self, "Select donation", "Select a donation first.")
            return
        donors = list_all_donors()
        dialog = DonationDialog(
            self, donors=donors, project_id=self.project_id, donation=donation
        )
        if dialog.exec():
            try:
                save_donation(donation.id, dialog.values())
                self.refresh()
                self._notify()
            except Exception as exc:
                QMessageBox.critical(self, "Save failed", str(exc))

    def remove_donation(self):
        donation_id = selected_id(self.table)
        if donation_id is None:
            QMessageBox.information(self, "Select donation", "Select a donation first.")
            return
        if (
            QMessageBox.question(self, "Confirm deletion", "Delete this donation?")
            != QMessageBox.StandardButton.Yes
        ):
            return
        try:
            delete_donation(donation_id)
            self.refresh()
            self._notify()
        except Exception as exc:
            QMessageBox.critical(self, "Delete failed", str(exc))
