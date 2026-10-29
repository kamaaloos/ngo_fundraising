from decimal import Decimal

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.auth.session import current_session
from app.db.repository import global_dashboard_stats
from app.i18n import td, tr
from app.utils import money
from app.widgets.stat_card import StatCard
from app.widgets.table_page import fill_table, make_table


class OverviewPage(QWidget):
    """Global home: all accessible projects."""

    def __init__(self, on_open_project=None):
        super().__init__()
        self.on_open_project = on_open_project
        self.setObjectName("contentArea")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 26, 28, 26)
        layout.setSpacing(16)

        title = QLabel(tr("overview.title"))
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        self.subtitle = QLabel(tr("overview.subtitle"))
        self.subtitle.setObjectName("muted")
        self.subtitle.setWordWrap(True)
        layout.addWidget(self.subtitle)

        self.cards = QHBoxLayout()
        self.cards.setSpacing(14)
        layout.addLayout(self.cards)

        self.card_projects = StatCard(
            tr("card.projects"), "0", tr("card.projects_hint"), accent="blue"
        )
        self.card_pledged = StatCard(
            tr("card.pledged"), "0.00", tr("card.pledged_hint"), accent="violet"
        )
        self.card_raised = StatCard(
            tr("card.raised"), "0.00", tr("card.raised_hint"), accent="teal"
        )
        self.card_outstanding = StatCard(
            tr("card.outstanding"), "0.00", tr("card.outstanding_hint"), accent="amber"
        )
        self.card_expenses = StatCard(
            tr("card.expenses"), "0.00", tr("card.expenses_hint"), accent="rose"
        )
        for card in (
            self.card_projects,
            self.card_pledged,
            self.card_raised,
            self.card_outstanding,
            self.card_expenses,
        ):
            self.cards.addWidget(card, 1)

        section = QLabel(tr("overview.projects"))
        section.setObjectName("sectionTitle")
        layout.addWidget(section)

        self.table = make_table(
            [
                tr("col.id"),
                tr("col.project"),
                tr("col.status"),
                tr("col.target"),
                tr("col.pledged"),
                tr("col.raised"),
                tr("col.outstanding"),
                tr("col.fund_status"),
                tr("col.progress"),
            ]
        )
        self.table.doubleClicked.connect(self._open_selected)
        layout.addWidget(self.table)

        bar = QHBoxLayout()
        open_btn = QPushButton(tr("overview.open_dashboard"))
        open_btn.setObjectName("primaryButton")
        open_btn.clicked.connect(self._open_selected)
        refresh = QPushButton(tr("common.refresh"))
        refresh.clicked.connect(self.refresh)
        bar.addWidget(open_btn)
        bar.addWidget(refresh)
        bar.addStretch()
        layout.addLayout(bar)

    def _open_selected(self):
        from app.widgets.table_page import selected_id

        project_id = selected_id(self.table)
        if project_id and self.on_open_project:
            self.on_open_project(project_id)

    def refresh(self):
        stats = global_dashboard_stats(
            role=current_session.role,
            project_ids=current_session.project_ids,
        )
        outstanding = stats["total_outstanding"]
        net = stats["total_raised"] - stats["total_expenses"]
        role = (
            tr("overview.role_admin")
            if current_session.is_admin
            else tr("overview.role_user")
        )
        self.subtitle.setText(
            tr(
                "overview.signed_in",
                name=current_session.full_name,
                role=role,
                donors=stats["donor_count"],
                outstanding=money(outstanding),
                net=money(net),
            )
        )
        self.card_projects.set_value(str(stats["project_count"]), tr("card.projects_hint"))
        self.card_pledged.set_value(
            money(stats["total_pledged"]), tr("card.pledged_hint")
        )
        self.card_raised.set_value(money(stats["total_raised"]), tr("card.raised_hint"))
        self.card_outstanding.set_value(
            money(outstanding), tr("card.outstanding_hint_detail")
        )
        self.card_expenses.set_value(
            money(stats["total_expenses"]), tr("card.expenses_hint")
        )

        fill_table(
            self.table,
            [
                (
                    p.id,
                    p.name,
                    td(p.status),
                    money(p.target_amount),
                    money(p.amount_pledged),
                    money(p.amount_raised),
                    money(
                        max(
                            Decimal("0"),
                            p.amount_pledged - p.amount_raised,
                        )
                    ),
                    td(p.fundraising_status),
                    f"{p.progress_percent:.0f}%",
                )
                for p in stats["projects"]
            ],
        )
