from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.db.repository import donor_project_summary
from app.utils import money
from app.widgets.stat_card import StatCard
from app.widgets.table_page import fill_table, make_table


class DonorDetailDialog(QDialog):
    """Full cross-project giving history for one donor, with pagination."""

    def __init__(self, parent=None, donor_id: int | None = None):
        super().__init__(parent)
        self.setWindowTitle("Donor profile")
        self.setWindowFlag(Qt.WindowType.WindowMaximizeButtonHint, True)
        self.setMinimumSize(960, 680)
        self.resize(1040, 760)

        self._projects: list[dict] = []
        self._donations: list[dict] = []
        self._project_page = 1
        self._donation_page = 1
        self._project_page_size = 5
        self._donation_page_size = 10

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(scroll.Shape.NoFrame)
        root.addWidget(scroll, 1)

        body = QWidget()
        scroll.setWidget(body)
        layout = QVBoxLayout(body)
        layout.setContentsMargins(24, 22, 24, 16)
        layout.setSpacing(14)

        self.title = QLabel("Donor")
        self.title.setObjectName("pageTitle")
        layout.addWidget(self.title)

        self.contact = QLabel("")
        self.contact.setObjectName("muted")
        self.contact.setWordWrap(True)
        self.contact.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        layout.addWidget(self.contact)

        cards = QHBoxLayout()
        cards.setSpacing(12)
        self.card_pledged = StatCard("TOTAL PLEDGED", "0.00", "All projects")
        self.card_paid = StatCard(
            "TOTAL PAID",
            "0.00",
            "Click for payment history",
            clickable=True,
        )
        self.card_paid.setToolTip(
            "Open payment history — times paid, received by, date, method…"
        )
        self.card_paid.clicked.connect(self._open_payments)
        self.card_remaining = StatCard("TOTAL REMAINING", "0.00", "Still outstanding")
        self.card_projects = StatCard("PROJECTS", "0", "Participated")
        for card in (
            self.card_pledged,
            self.card_paid,
            self.card_remaining,
            self.card_projects,
        ):
            cards.addWidget(card)
        layout.addLayout(cards)

        by_project = QLabel("By project")
        by_project.setObjectName("sectionTitle")
        layout.addWidget(by_project)

        self.project_table = make_table(
            [
                "Project",
                "First pledge",
                "Last activity",
                "Pledged",
                "Paid",
                "Remaining",
                "Donations",
            ]
        )
        self.project_table.setMinimumHeight(160)
        layout.addWidget(self.project_table)

        (
            self.project_prev,
            self.project_next,
            self.project_label,
            self.project_size_combo,
            project_bar,
        ) = self._build_pager(
            on_prev=self._prev_projects,
            on_next=self._next_projects,
            on_size=self._on_project_page_size,
            default_size=5,
            sizes=(5, 10, 25),
        )
        layout.addLayout(project_bar)

        by_donation = QLabel("All donations (dated)")
        by_donation.setObjectName("sectionTitle")
        layout.addWidget(by_donation)

        self.donation_table = make_table(
            [
                "ID",
                "Date",
                "Project",
                "Pledged",
                "Paid",
                "Remaining",
                "Method",
                "Status",
                "Reference",
                "Notes",
            ]
        )
        self.donation_table.setMinimumHeight(240)
        self.donation_table.doubleClicked.connect(self._open_donation_payments)
        layout.addWidget(self.donation_table)

        tip = QLabel("Tip: click TOTAL PAID, or double-click a donation row, for payment details.")
        tip.setObjectName("muted")
        layout.addWidget(tip)

        (
            self.donation_prev,
            self.donation_next,
            self.donation_label,
            self.donation_size_combo,
            donation_bar,
        ) = self._build_pager(
            on_prev=self._prev_donations,
            on_next=self._next_donations,
            on_size=self._on_donation_page_size,
            default_size=10,
            sizes=(5, 10, 25, 50),
        )
        layout.addLayout(donation_bar)

        footer = QHBoxLayout()
        footer.setContentsMargins(24, 8, 24, 16)
        export_xls = QPushButton("Export Excel")
        export_xls.setObjectName("ghostButton")
        export_xls.clicked.connect(self.export_excel)
        export_pdf = QPushButton("Export PDF")
        export_pdf.setObjectName("ghostButton")
        export_pdf.clicked.connect(self.export_pdf)
        close_btn = QPushButton("Close")
        close_btn.setObjectName("primaryButton")
        close_btn.clicked.connect(self.accept)
        footer.addWidget(export_xls)
        footer.addWidget(export_pdf)
        footer.addStretch()
        footer.addWidget(close_btn)
        root.addLayout(footer)

        self._donor_id = donor_id
        if donor_id is not None:
            self.load(donor_id)

    @staticmethod
    def _build_pager(on_prev, on_next, on_size, default_size, sizes):
        bar = QHBoxLayout()
        prev_btn = QPushButton("‹ Previous")
        prev_btn.clicked.connect(on_prev)
        next_btn = QPushButton("Next ›")
        next_btn.clicked.connect(on_next)
        label = QLabel("Page 1")
        label.setObjectName("muted")
        size_combo = QComboBox()
        for size in sizes:
            size_combo.addItem(str(size), size)
        index = list(sizes).index(default_size) if default_size in sizes else 0
        size_combo.setCurrentIndex(index)
        size_combo.currentIndexChanged.connect(on_size)
        bar.addWidget(prev_btn)
        bar.addWidget(next_btn)
        bar.addWidget(label)
        bar.addStretch()
        bar.addWidget(QLabel("Per page"))
        bar.addWidget(size_combo)
        return prev_btn, next_btn, label, size_combo, bar

    def load(self, donor_id: int):
        summary = donor_project_summary(donor_id)
        donor = summary["donor"]
        self.setWindowTitle(f"Donor — {donor.name}")
        self.title.setText(donor.name)

        contact_parts = [
            p
            for p in (
                donor.email or "",
                donor.phone or "",
                donor.address or "",
            )
            if p
        ]
        notes = (donor.notes or "").strip()
        contact_text = " · ".join(contact_parts) if contact_parts else "No contact details"
        if notes:
            contact_text += f"\nNotes: {notes}"
        self.contact.setText(contact_text)

        self.card_pledged.set_value(money(summary["total_pledged"]), "All projects")
        self.card_paid.set_value(
            money(summary["total_paid"]), "Click for payment history"
        )
        self.card_remaining.set_value(
            money(summary["total_remaining"]), "Still outstanding"
        )
        self.card_projects.set_value(
            str(summary["project_count"]),
            f"{summary['donation_count']} donation(s)",
        )

        self._projects = list(summary["projects"])
        self._donations = list(summary["donations"])
        self._project_page = 1
        self._donation_page = 1
        self._render_projects()
        self._render_donations()

    def _slice(self, rows: list, page: int, page_size: int):
        total = len(rows)
        max_page = max(1, (total + page_size - 1) // page_size) if total else 1
        page = min(max(1, page), max_page)
        start = (page - 1) * page_size
        return rows[start : start + page_size], total, page, max_page

    def _render_projects(self):
        page_rows, total, page, max_page = self._slice(
            self._projects, self._project_page, self._project_page_size
        )
        self._project_page = page
        fill_table(
            self.project_table,
            [
                (
                    row["project_name"],
                    row["first_date"].isoformat(),
                    row["last_date"].isoformat(),
                    money(row["pledged"]),
                    money(row["paid"]),
                    money(row["remaining"]),
                    row["donations"],
                )
                for row in page_rows
            ],
        )
        self.project_label.setText(
            f"Page {page} of {max_page} · {total} project(s)"
        )
        self.project_prev.setEnabled(page > 1)
        self.project_next.setEnabled(page < max_page)

    def _render_donations(self):
        page_rows, total, page, max_page = self._slice(
            self._donations, self._donation_page, self._donation_page_size
        )
        self._donation_page = page
        fill_table(
            self.donation_table,
            [
                (
                    row["id"],
                    row["date"].isoformat(),
                    row["project_name"],
                    money(row["pledged"]),
                    money(row["paid"]),
                    money(row["remaining"]),
                    row["method"],
                    row["status"],
                    row["reference"] or "—",
                    (row.get("notes") or "—"),
                )
                for row in page_rows
            ],
        )
        self.donation_label.setText(
            f"Page {page} of {max_page} · {total} donation(s)"
        )
        self.donation_prev.setEnabled(page > 1)
        self.donation_next.setEnabled(page < max_page)

    def _open_payments(self):
        from app.dialogs.payment_history_dialog import PaymentHistoryDialog

        if self._donor_id is None:
            return
        PaymentHistoryDialog(self, donor_id=self._donor_id).exec()

    def _open_donation_payments(self):
        from app.dialogs.payment_history_dialog import PaymentHistoryDialog
        from app.widgets.table_page import selected_id

        donation_id = selected_id(self.donation_table)
        if donation_id is None:
            return
        PaymentHistoryDialog(self, donation_id=donation_id).exec()

    def _prev_projects(self):
        if self._project_page > 1:
            self._project_page -= 1
            self._render_projects()

    def _next_projects(self):
        self._project_page += 1
        self._render_projects()

    def _prev_donations(self):
        if self._donation_page > 1:
            self._donation_page -= 1
            self._render_donations()

    def _next_donations(self):
        self._donation_page += 1
        self._render_donations()

    def _on_project_page_size(self, *_):
        self._project_page_size = self.project_size_combo.currentData() or 5
        self._project_page = 1
        self._render_projects()

    def _on_donation_page_size(self, *_):
        self._donation_page_size = self.donation_size_combo.currentData() or 10
        self._donation_page = 1
        self._render_donations()

    def export_excel(self):
        from PySide6.QtWidgets import QFileDialog, QMessageBox
        from app.db.repository import get_donor
        from app.io.exporters import export_donors_xlsx

        if not self._donor_id:
            return
        donor = get_donor(self._donor_id)
        if donor is None:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Excel", f"donor_{donor.id}.xlsx", "Excel (*.xlsx)"
        )
        if not path:
            return
        try:
            export_donors_xlsx(path, [donor])
            QMessageBox.information(self, "Export complete", f"Saved:\n{path}")
        except Exception as exc:
            QMessageBox.critical(self, "Export failed", str(exc))

    def export_pdf(self):
        from PySide6.QtWidgets import QFileDialog, QMessageBox
        from app.db.repository import get_donor
        from app.io.exporters import export_donors_pdf

        if not self._donor_id:
            return
        donor = get_donor(self._donor_id)
        if donor is None:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Export PDF", f"donor_{donor.id}.pdf", "PDF (*.pdf)"
        )
        if not path:
            return
        try:
            export_donors_pdf(path, [donor], title=f"Donor — {donor.name}")
            QMessageBox.information(self, "Export complete", f"Saved:\n{path}")
        except Exception as exc:
            QMessageBox.critical(self, "Export failed", str(exc))
