from decimal import Decimal

from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.db.repository import get_project, list_donations
from app.i18n import td, tr
from app.utils import money
from app.widgets.stat_card import StatCard
from app.widgets.table_page import fill_table, make_table


class ProjectDashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("contentArea")
        self.project_id: int | None = None
        self._donations: list = []
        self._page = 1
        self._page_size = 10

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        outer.addWidget(scroll)

        body = QWidget()
        scroll.setWidget(body)
        layout = QVBoxLayout(body)
        layout.setContentsMargins(28, 26, 28, 26)
        layout.setSpacing(16)

        self.title = QLabel(tr("project_dashboard.title"))
        self.title.setObjectName("pageTitle")
        layout.addWidget(self.title)

        self.subtitle = QLabel(tr("project_dashboard.select"))
        self.subtitle.setObjectName("muted")
        self.subtitle.setWordWrap(True)
        layout.addWidget(self.subtitle)

        cards = QHBoxLayout()
        cards.setSpacing(14)
        self.card_target = StatCard(
            tr("card.target"), "0.00", tr("card.target_hint"), accent="blue"
        )
        self.card_raised = StatCard(
            tr("card.raised"), "0.00", tr("card.raised_paid_hint"), accent="teal"
        )
        self.card_pledged = StatCard(
            tr("card.pledged"),
            "0.00",
            tr("card.pledged_committed_hint"),
            accent="violet",
        )
        self.card_outstanding = StatCard(
            tr("card.outstanding"),
            "0.00",
            tr("card.outstanding_owed_hint"),
            accent="amber",
        )
        self.card_expenses = StatCard(
            tr("card.expenses"),
            "0.00",
            tr("card.expenses_project_hint"),
            accent="rose",
        )
        for card in (
            self.card_target,
            self.card_raised,
            self.card_pledged,
            self.card_outstanding,
            self.card_expenses,
        ):
            cards.addWidget(card, 1)
        layout.addLayout(cards)

        progress_panel = QFrame()
        progress_panel.setObjectName("panel")
        progress_layout = QVBoxLayout(progress_panel)
        progress_layout.setContentsMargins(18, 16, 18, 16)
        progress_layout.setSpacing(10)

        self.progress_label = QLabel(tr("project_dashboard.progress"))
        self.progress_label.setObjectName("sectionTitle")
        progress_layout.addWidget(self.progress_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        progress_layout.addWidget(self.progress_bar)

        self.fund_status = QLabel("")
        self.fund_status.setObjectName("muted")
        self.fund_status.setWordWrap(True)
        progress_layout.addWidget(self.fund_status)
        layout.addWidget(progress_panel)

        recent_panel = QFrame()
        recent_panel.setObjectName("panel")
        recent_layout = QVBoxLayout(recent_panel)
        recent_layout.setContentsMargins(18, 16, 18, 16)
        recent_layout.setSpacing(12)

        recent_header = QHBoxLayout()
        recent = QLabel(tr("project_dashboard.recent"))
        recent.setObjectName("sectionTitle")
        recent_header.addWidget(recent)
        recent_header.addStretch()
        recent_header.addWidget(QLabel(tr("project_dashboard.per_page")))
        self.page_size_combo = QComboBox()
        for size in (5, 10, 25, 50):
            self.page_size_combo.addItem(str(size), size)
        self.page_size_combo.setCurrentIndex(1)
        self.page_size_combo.currentIndexChanged.connect(self._on_page_size_changed)
        recent_header.addWidget(self.page_size_combo)
        recent_layout.addLayout(recent_header)

        self.table = make_table(
            [
                tr("col.id"),
                tr("col.date"),
                tr("col.donor"),
                tr("col.pledged"),
                tr("col.paid"),
                tr("col.remaining"),
                tr("col.method"),
                tr("col.status"),
            ]
        )
        recent_layout.addWidget(self.table)

        pager = QHBoxLayout()
        self.prev_btn = QPushButton(tr("common.previous"))
        self.prev_btn.clicked.connect(self._prev_page)
        self.next_btn = QPushButton(tr("common.next"))
        self.next_btn.clicked.connect(self._next_page)
        self.page_label = QLabel("")
        self.page_label.setObjectName("muted")
        pager.addWidget(self.prev_btn)
        pager.addWidget(self.next_btn)
        pager.addWidget(self.page_label)
        pager.addStretch()
        recent_layout.addLayout(pager)
        layout.addWidget(recent_panel)
        layout.addStretch()

    def set_project(self, project_id: int | None):
        self.project_id = project_id
        self._page = 1
        self.refresh()

    def _on_page_size_changed(self, *_):
        self._page_size = self.page_size_combo.currentData() or 10
        self._page = 1
        self._render_donations_page()

    def _prev_page(self):
        if self._page > 1:
            self._page -= 1
            self._render_donations_page()

    def _next_page(self):
        total = len(self._donations)
        max_page = max(1, (total + self._page_size - 1) // self._page_size)
        if self._page < max_page:
            self._page += 1
            self._render_donations_page()

    def _render_donations_page(self):
        total = len(self._donations)
        max_page = max(1, (total + self._page_size - 1) // self._page_size) if total else 1
        self._page = min(max(1, self._page), max_page)
        start = (self._page - 1) * self._page_size
        page_rows = self._donations[start : start + self._page_size]

        fill_table(
            self.table,
            [
                (
                    d.id,
                    d.donation_date.isoformat(),
                    d.donor.name if d.donor else "",
                    money(d.pledged_amount),
                    money(d.paid_amount),
                    money(d.remaining_amount),
                    td(d.payment_method),
                    td(d.status),
                )
                for d in page_rows
            ],
        )
        self.page_label.setText(
            tr(
                "project_dashboard.page",
                page=self._page,
                max_page=max_page,
                total=total,
            )
        )
        self.prev_btn.setEnabled(self._page > 1)
        self.next_btn.setEnabled(self._page < max_page)

    def refresh(self):
        if self.project_id is None:
            self.title.setText(tr("project_dashboard.title"))
            self.subtitle.setText(tr("project_dashboard.select"))
            self.card_target.set_value("0.00")
            self.card_raised.set_value("0.00")
            self.card_pledged.set_value("0.00")
            self.card_outstanding.set_value("0.00")
            self.card_expenses.set_value("0.00")
            self.progress_bar.setValue(0)
            self.fund_status.setText("")
            self._donations = []
            self._page = 1
            self._render_donations_page()
            return

        project = get_project(self.project_id)
        if project is None:
            self.subtitle.setText(tr("project_dashboard.not_found"))
            return

        outstanding = project.amount_pledged - project.amount_raised
        if outstanding < 0:
            outstanding = Decimal("0.00")

        self.title.setText(project.name)
        self.subtitle.setText(
            project.description
            or tr(
                "project_dashboard.status_line",
                status=td(project.status),
                fund_status=td(project.fundraising_status),
            )
        )
        self.card_target.set_value(money(project.target_amount), tr("card.target_hint"))
        self.card_raised.set_value(
            money(project.amount_raised), tr("card.raised_paid_hint")
        )
        self.card_pledged.set_value(
            money(project.amount_pledged), tr("card.pledged_committed_hint")
        )
        self.card_outstanding.set_value(
            money(outstanding), tr("card.outstanding_owed_hint")
        )
        self.card_expenses.set_value(
            money(project.total_expenses), tr("card.expenses_project_hint")
        )

        pct = int(round(project.progress_percent))
        self.progress_bar.setValue(pct)
        remaining_to_target = money(project.remaining_to_target)
        self.fund_status.setText(
            tr(
                "project_dashboard.fund_line",
                fund_status=td(project.fundraising_status),
                pct=pct,
                remaining=remaining_to_target,
                outstanding=money(outstanding),
                donors=project.unique_donor_count,
                donations=project.donation_count,
            )
        )

        self._donations = list_donations(self.project_id)
        self._render_donations_page()
