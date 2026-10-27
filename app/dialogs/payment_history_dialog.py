from decimal import Decimal

from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.database import SessionLocal
from app.db.models import Donation
from app.db.repository import get_donor, list_donation_payments, list_donor_payments
from app.utils import money
from app.widgets.stat_card import StatCard
from app.widgets.table_page import fill_table, make_table


class PaymentHistoryDialog(QDialog):
    """Shows how many times a donor (or one pledge) paid, by whom, when, method."""

    def __init__(
        self,
        parent=None,
        *,
        donor_id: int | None = None,
        donation_id: int | None = None,
        title: str | None = None,
    ):
        super().__init__(parent)
        self.setMinimumSize(860, 520)
        self.resize(920, 560)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 16)
        layout.setSpacing(12)

        self.heading = QLabel(title or "Payment history")
        self.heading.setObjectName("pageTitle")
        layout.addWidget(self.heading)

        self.subtitle = QLabel("")
        self.subtitle.setObjectName("muted")
        self.subtitle.setWordWrap(True)
        layout.addWidget(self.subtitle)

        cards = QHBoxLayout()
        cards.setSpacing(12)
        self.card_pledged = StatCard(
            "PLEDGED", "0.00", "Committed total", accent="violet"
        )
        self.card_total = StatCard(
            "TOTAL PAID", "0.00", "Across installments", accent="teal"
        )
        self.card_remaining = StatCard(
            "REMAINING", "0.00", "Still outstanding", accent="amber"
        )
        self.card_count = StatCard("PAYMENTS", "0", "Times paid", accent="blue")
        for card in (
            self.card_pledged,
            self.card_total,
            self.card_remaining,
            self.card_count,
        ):
            cards.addWidget(card, 1)
        layout.addLayout(cards)

        self.table = make_table(
            [
                "#",
                "Date",
                "Amount",
                "Pledged",
                "Method",
                "Received by",
                "Project",
                "Pledge status",
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

        if donation_id is not None:
            self._load_donation(donation_id)
        elif donor_id is not None:
            self._load_donor(donor_id)

    def _load_donor(self, donor_id: int):
        donor = get_donor(donor_id)
        name = donor.name if donor else f"Donor #{donor_id}"
        self.setWindowTitle(f"Payments — {name}")
        self.heading.setText(f"Payments · {name}")
        rows = list_donor_payments(donor_id)
        self._fill(rows, scope_note="All recorded installments for this donor")

    def _load_donation(self, donation_id: int):
        payments = list_donation_payments(donation_id)
        project_name = ""
        donor_name = ""
        status = ""
        pledged = Decimal("0")
        paid_total = Decimal("0")
        with SessionLocal() as session:
            donation = session.scalar(
                select(Donation)
                .options(
                    selectinload(Donation.project),
                    selectinload(Donation.donor),
                )
                .where(Donation.id == donation_id)
            )
            if donation is not None:
                project_name = donation.project.name if donation.project else ""
                donor_name = donation.donor.name if donation.donor else ""
                status = donation.status or ""
                pledged = Decimal(str(donation.pledged_amount))
                paid_total = Decimal(str(donation.paid_amount))

        self.setWindowTitle(f"Payments — pledge #{donation_id}")
        self.heading.setText(
            f"Payments · {donor_name}" if donor_name else f"Payments · pledge #{donation_id}"
        )
        rows = [
            {
                **row,
                "project_name": project_name,
                "status": status,
                "pledged": pledged,
                "donation_paid": paid_total,
            }
            for row in payments
        ]
        self._fill(
            rows,
            scope_note=f"Installments for donation #{donation_id}",
            pledged_override=pledged,
            paid_override=paid_total,
        )

    def _fill(
        self,
        rows: list[dict],
        scope_note: str,
        *,
        pledged_override: Decimal | None = None,
        paid_override: Decimal | None = None,
    ):
        paid_installments = sum((r["amount"] for r in rows), Decimal("0"))
        if pledged_override is not None:
            pledged = pledged_override
        else:
            # Donor view: one pledged total per donation (not per installment).
            by_donation: dict[int, Decimal] = {}
            for r in rows:
                did = r.get("donation_id")
                if did is None:
                    continue
                by_donation[int(did)] = Decimal(str(r.get("pledged") or 0))
            pledged = sum(by_donation.values(), Decimal("0"))

        if paid_override is not None:
            paid = paid_override
        else:
            by_paid: dict[int, Decimal] = {}
            for r in rows:
                did = r.get("donation_id")
                if did is None:
                    continue
                by_paid[int(did)] = Decimal(str(r.get("donation_paid") or 0))
            paid = (
                sum(by_paid.values(), Decimal("0"))
                if by_paid
                else paid_installments
            )

        remaining = pledged - paid
        if remaining < 0:
            remaining = Decimal("0")

        self.card_pledged.set_value(money(pledged), "Committed total")
        self.card_total.set_value(money(paid_installments), "Across installments")
        self.card_remaining.set_value(money(remaining), "Still outstanding")
        self.card_count.set_value(str(len(rows)), "Times paid")
        self.subtitle.setText(
            f"{scope_note} · pledged {money(pledged)} · "
            f"{len(rows)} payment(s) · {money(paid_installments)} received · "
            f"{money(remaining)} remaining"
        )

        fill_table(
            self.table,
            [
                (
                    idx,
                    r["date"].isoformat()
                    if hasattr(r["date"], "isoformat")
                    else r["date"],
                    money(r["amount"]),
                    money(r.get("pledged") or 0),
                    r.get("method") or "",
                    r.get("received_by") or "—",
                    r.get("project_name") or "—",
                    r.get("status") or "—",
                    r.get("reference") or "",
                    r.get("notes") or "",
                )
                for idx, r in enumerate(rows, start=1)
            ],
        )
