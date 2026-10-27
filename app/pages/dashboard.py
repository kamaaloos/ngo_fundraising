from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
                               QProgressBar, QScrollArea)
from app.widgets.stat_card import StatCard
from app.db.repository import list_projects


class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        outer.addWidget(scroll)
        body = QWidget()
        body.setObjectName('contentArea')
        scroll.setWidget(body)
        self.layout = QVBoxLayout(body)
        self.layout.setContentsMargins(30, 28, 30, 30)
        self.layout.setSpacing(20)
        title = QLabel('Fundraising Dashboard')
        title.setObjectName('pageTitle')
        self.layout.addWidget(title)
        subtitle = QLabel('Live project overview • Donors, donations and expenses arrive in later phases')
        subtitle.setObjectName('muted')
        subtitle.setWordWrap(True)
        self.layout.addWidget(subtitle)
        self.cards = QHBoxLayout()
        self.layout.addLayout(self.cards)
        self.projects_card = QFrame()
        self.projects_card.setObjectName('card')
        self.project_layout = QVBoxLayout(self.projects_card)
        self.project_layout.setContentsMargins(20, 20, 20, 20)
        self.layout.addWidget(self.projects_card)
        self.layout.addStretch()
        self.refresh()

    @staticmethod
    def clear_layout(layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                DashboardPage.clear_layout(item.layout())

    def refresh(self):
        projects = list_projects()
        self.clear_layout(self.cards)
        self.clear_layout(self.project_layout)
        active = sum(p.status == 'Active' for p in projects)
        total_goal = sum((p.goal for p in projects), 0)
        total_raised = sum((p.raised for p in projects), 0)
        total_budget = sum((p.budget for p in projects), 0)
        for title, value, note in [
            ('Projects', str(len(projects)), 'Saved in SQLite'),
            ('Active Projects', str(active), 'Currently active'),
            ('Fundraising Goal', f'€{total_goal:,.2f}', 'All projects'),
            ('Raised (manual)', f'€{total_raised:,.2f}', 'Entered in project forms'),
            ('Planned Budget', f'€{total_budget:,.2f}', 'Not actual expenses'),
        ]:
            self.cards.addWidget(StatCard(title, value, note), 1)
        heading = QLabel('Project Fundraising Progress')
        heading.setObjectName('sectionTitle')
        self.project_layout.addWidget(heading)
        if not projects:
            self.project_layout.addWidget(QLabel('No projects yet. Open Projects → New Project to get started.'))
        for project in projects:
            line = QHBoxLayout()
            line.addWidget(QLabel(project.name))
            line.addStretch()
            line.addWidget(QLabel(f'€{project.raised:,.2f} / €{project.goal:,.2f}'))
            self.project_layout.addLayout(line)
            bar = QProgressBar()
            bar.setRange(0, 100)
            bar.setValue(min(100, round(float(project.raised / project.goal * 100))) if project.goal else 0)
            bar.setFormat('%p%')
            self.project_layout.addWidget(bar)
