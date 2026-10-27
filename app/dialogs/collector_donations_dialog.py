"""Search a staff user and list every donation they collected."""

from __future__ import annotations

from decimal import Decimal

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from app.db.repository import list_collector_choices, list_donations_by_collector
from app.utils import money
from app.widgets.stat_card import StatCard
from app.widgets.table_page import fill_table, make_table


class CollectorDonationsDialog(QDialog):
    def __init__(self, parent=None, *, project_id: int | None = None):
        super().__init__(parent)
        self.project_id = project_id
        self.setWindowTitle("Donations by collector")
        self.setMinimumSize(920, 560)
        self.resize(980, 600)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 16)
        layout.setSpacing(12)

        heading = QLabel("Who collected — donation details")
        heading.setObjectName("pageTitle")
        layout.addWidget(heading)

        self.subtitle = QLabel(
            "Pick a staff user to see every donation they collected, "
            "with donor, amounts, method, and status."
        )
        self.subtitle.setObjectName("muted")
        self.subtitle.setWordWrap(True)
        layout.addWidget(self.subtitle)

        picker = QHBoxLayout()
        picker.addWidget(QLabel("Collected by"))
        self.collector = QComboBox()
        self.collector.setEditable(True)
        self.collector.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.collector.lineEdit().setPlaceholderText("Search staff…")
        self.collector.addItem("Select staff…", None)
        for user in list_collector_choices():
            label = user.display_name
            if user.username and user.username.lower() != label.lower():
                label = f"{label}  (@{user.username})"
            self.collector.addItem(label, user.id)
        self.collector.currentIndexChanged.connect(self._reload)
        picker.addWidget(self.collector, 1)
        layout.addLayout(picker)

        cards = QHBoxLayout()
        cards.setSpacing(12)
        self.card_count = StatCard("DONATIONS", "0", "Collected", accent="blue")
        self.card_pledged = StatCard("PLEDGED", "0.00", "Total", accent="violet")
        self.card_paid = StatCard("PAID", "0.00", "Collected cash", accent="teal")
        for card in (self.card_count, self.card_pledged, self.card_paid):
            cards.addWidget(card, 1)
        layout.addLayout(cards)

        self.table = make_table(
            [
                "ID",
                "Date",
                "Project",
                "Donor",
                "Pledged",
                "Paid",
                "Remaining",
                "Method",
                "Status",
                "Reference",
                "Notes",
            ]
        )
        layout.addWidget(self.table, 1)

        footer = QHBoxLayout()
        footer.addStretch()
        close_btn = QPushButton("Close")
        close_btn.setObjectName("primaryButton")
        close_btn.clicked.connect(self.accept)
        footer.addWidget(close_btn)
        layout.addLayout(footer)

        self._reload()

    def _reload(self):
        user_id = self.collector.currentData()
        if user_id is None:
            fill_table(self.table, [])
            self.card_count.set_value("0")
            self.card_pledged.set_value("0.00")
            self.card_paid.set_value("0.00")
            scope = "this project" if self.project_id else "all accessible projects"
            self.subtitle.setText(
                f"Pick a staff user to list donations they collected ({scope})."
            )
            return

        rows = list_donations_by_collector(int(user_id), project_id=self.project_id)
        fill_table(
            self.table,
            [
                (
                    d.id,
                    d.donation_date.isoformat(),
                    d.project.name if d.project else f"#{d.project_id}",
                    d.donor.name if d.donor else "",
                    money(d.pledged_amount),
                    money(d.paid_amount),
                    money(d.remaining_amount),
                    d.payment_method or "",
                    d.status or "",
                    d.reference or "",
                    (d.notes or "")[:80],
                )
                for d in rows
            ],
        )
        pledged = sum((Decimal(str(d.pledged_amount)) for d in rows), Decimal("0"))
        paid = sum((Decimal(str(d.paid_amount)) for d in rows), Decimal("0"))
        self.card_count.set_value(str(len(rows)))
        self.card_pledged.set_value(money(pledged))
        self.card_paid.set_value(money(paid))
        name = self.collector.currentText().split("  (")[0]
        scope = "this project" if self.project_id else "accessible projects"
        self.subtitle.setText(
            f"{len(rows)} donation(s) collected by {name} · {scope}"
        )
