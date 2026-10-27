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

        title = QLabel("Overview")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        self.subtitle = QLabel("Your fundraising portfolio")
        self.subtitle.setObjectName("muted")
        self.subtitle.setWordWrap(True)
        layout.addWidget(self.subtitle)

        self.cards = QHBoxLayout()
        self.cards.setSpacing(14)
        layout.addLayout(self.cards)

        self.card_projects = StatCard("PROJECTS", "0", "Accessible to you", accent="blue")
        self.card_pledged = StatCard(
            "PLEDGED", "0.00", "Committed by donors", accent="violet"
        )
        self.card_raised = StatCard("RAISED", "0.00", "Already paid", accent="teal")
        self.card_outstanding = StatCard(
            "OUTSTANDING", "0.00", "Still owed by donors", accent="amber"
        )
        self.card_expenses = StatCard(
            "EXPENSES", "0.00", "Recorded spend", accent="rose"
        )
        for card in (
            self.card_projects,
            self.card_pledged,
            self.card_raised,
            self.card_outstanding,
            self.card_expenses,
        ):
            self.cards.addWidget(card, 1)

        section = QLabel("Projects")
        section.setObjectName("sectionTitle")
        layout.addWidget(section)

        self.table = make_table(
            [
                "ID",
                "Project",
                "Status",
                "Target",
                "Pledged",
                "Raised",
                "Outstanding",
                "Fund status",
                "Progress",
            ]
        )
        self.table.doubleClicked.connect(self._open_selected)
        layout.addWidget(self.table)

        bar = QHBoxLayout()
        open_btn = QPushButton("Open project dashboard")
        open_btn.setObjectName("primaryButton")
        open_btn.clicked.connect(self._open_selected)
        refresh = QPushButton("Refresh")
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
        self.subtitle.setText(
            f"Signed in as {current_session.full_name} · "
            f"{'Administrator' if current_session.is_admin else 'Project user'} · "
            f"{stats['donor_count']} donor(s) · "
            f"Outstanding (donors still owe): {money(outstanding)} · "
            f"Cash net (raised − expenses): {money(net)}"
        )
        self.card_projects.set_value(str(stats["project_count"]), "Accessible to you")
        self.card_pledged.set_value(
            money(stats["total_pledged"]), "Committed by donors"
        )
        self.card_raised.set_value(money(stats["total_raised"]), "Already paid")
        self.card_outstanding.set_value(
            money(outstanding), "Pledged − raised (donors still owe)"
        )
        self.card_expenses.set_value(money(stats["total_expenses"]), "Recorded spend")

        fill_table(
            self.table,
            [
                (
                    p.id,
                    p.name,
                    p.status,
                    money(p.target_amount),
                    money(p.amount_pledged),
                    money(p.amount_raised),
                    money(
                        max(
                            Decimal("0"),
                            p.amount_pledged - p.amount_raised,
                        )
                    ),
                    p.fundraising_status,
                    f"{p.progress_percent:.0f}%",
                )
                for p in stats["projects"]
            ],
        )
