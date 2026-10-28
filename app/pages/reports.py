from decimal import Decimal

from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app.auth.session import current_session
from app.db.repository import portfolio_report_stats, project_report_stats
from app.i18n import tr
from app.io.report_print import export_report_pdf, print_report
from app.utils import money
from app.widgets.chart_hover import enable_bar_hover, enable_line_hover
from app.widgets.hover_frame import HoverFrame
from app.widgets.stat_card import StatCard

FigureCanvas = None  # type: ignore
Figure = None  # type: ignore
HAS_MPL = False
_MPL_IMPORT_ERROR = ""


def _ensure_matplotlib() -> bool:
    """Lazy-import matplotlib after QApplication exists (required for QtAgg)."""
    global FigureCanvas, Figure, HAS_MPL, _MPL_IMPORT_ERROR
    if HAS_MPL and FigureCanvas is not None and Figure is not None:
        return True
    try:
        from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as _Canvas
        from matplotlib.figure import Figure as _Figure

        FigureCanvas = _Canvas
        Figure = _Figure
        HAS_MPL = True
        _MPL_IMPORT_ERROR = ""
        return True
    except Exception as exc:  # noqa: BLE001 — show in UI for frozen builds
        FigureCanvas = None
        Figure = None
        HAS_MPL = False
        _MPL_IMPORT_ERROR = f"{type(exc).__name__}: {exc}"
        return False


def _charts_unavailable_message(extra: str = "") -> str:
    detail = _MPL_IMPORT_ERROR or "matplotlib could not be loaded"
    base = (
        "Charts are unavailable in this install.\n"
        f"({detail})"
    )
    if extra:
        return f"{base}\n{extra}"
    return base

# Distinct colors so each project is easy to tell apart on overall charts.
PROJECT_COLORS = [
    "#176B5B",
    "#2B6CB0",
    "#C05621",
    "#6B46C1",
    "#B83280",
    "#2C7A7B",
    "#DD6B20",
    "#3182CE",
    "#38A169",
    "#D69E2E",
    "#E53E3E",
    "#805AD5",
    "#319795",
    "#DD6B20",
    "#4A5568",
]


class ReportsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.project_id: int | None = None
        self.setObjectName("contentArea")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(scroll.Shape.NoFrame)
        outer.addWidget(scroll)

        body = QWidget()
        scroll.setWidget(body)
        layout = QVBoxLayout(body)
        layout.setContentsMargins(28, 26, 28, 26)
        layout.setSpacing(16)

        top = QHBoxLayout()
        title = QLabel(tr("reports.title"))
        title.setObjectName("pageTitle")
        top.addWidget(title)
        top.addStretch()

        self.scope_label = QLabel("View")
        self.scope_combo = QComboBox()
        self.scope_combo.addItem("Overall (all projects)", "overall")
        self.scope_combo.addItem("This project only", "project")
        self.scope_combo.currentIndexChanged.connect(self.refresh)
        top.addWidget(self.scope_label)
        top.addWidget(self.scope_combo)

        refresh = QPushButton("Refresh charts")
        refresh.clicked.connect(self.refresh)
        top.addWidget(refresh)

        self.print_btn = QPushButton("Print…")
        self.print_btn.setObjectName("ghostButton")
        self.print_btn.setToolTip("Print the current report summary and charts")
        self.print_btn.clicked.connect(self.print_current_report)
        top.addWidget(self.print_btn)

        self.pdf_btn = QPushButton("Save PDF")
        self.pdf_btn.setObjectName("primaryButton")
        self.pdf_btn.setToolTip("Save summary + all charts as a PDF file")
        self.pdf_btn.clicked.connect(self.save_current_report_pdf)
        top.addWidget(self.pdf_btn)
        layout.addLayout(top)

        self.subtitle = QLabel("Graphical fundraising insights.")
        self.subtitle.setObjectName("muted")
        self.subtitle.setWordWrap(True)
        layout.addWidget(self.subtitle)

        cards = QHBoxLayout()
        cards.setSpacing(14)
        self.card_target = StatCard("TARGET", "0.00", "Fundraising goal", accent="blue")
        self.card_raised = StatCard("RAISED", "0.00", "Paid amount", accent="teal")
        self.card_pledged = StatCard("PLEDGED", "0.00", "Committed amount", accent="violet")
        self.card_outstanding = StatCard(
            "OUTSTANDING", "0.00", "Still owed by donors", accent="amber"
        )
        self.card_expenses = StatCard(
            "EXPENSES", "0.00", "Project spend", accent="rose"
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

        self.charts_container = QWidget()
        self.charts_layout = QGridLayout(self.charts_container)
        self.charts_layout.setContentsMargins(0, 0, 0, 0)
        self.charts_layout.setHorizontalSpacing(14)
        self.charts_layout.setVerticalSpacing(14)
        layout.addWidget(self.charts_container)
        layout.addStretch()

        self._figures: list = []
        self._report_title = "Reports"
        self._report_subtitle = ""
        self._report_cards: list[tuple[str, str, str]] = []

    def set_project(self, project_id: int | None):
        self.project_id = project_id
        self._configure_scope()
        self.refresh()

    def _set_report_snapshot(
        self,
        title: str,
        subtitle: str,
        cards: list[tuple[str, str, str]],
    ):
        self._report_title = title
        self._report_subtitle = subtitle
        self._report_cards = list(cards)

    def _has_printable_report(self) -> bool:
        return bool(self._figures) or bool(self._report_cards)

    def print_current_report(self):
        if not self._has_printable_report():
            QMessageBox.information(
                self,
                "Print",
                "Nothing to print yet. Refresh charts for Overall or a project first.",
            )
            return
        try:
            ok = print_report(
                self,
                title=self._report_title,
                subtitle=self._report_subtitle,
                cards=self._report_cards,
                figures=list(self._figures),
            )
        except Exception as exc:
            QMessageBox.critical(self, "Print failed", str(exc))
            return
        if ok:
            QMessageBox.information(self, "Print", "Report sent to the printer.")

    def save_current_report_pdf(self):
        if not self._has_printable_report():
            QMessageBox.information(
                self,
                "Save PDF",
                "Nothing to save yet. Refresh charts for Overall or a project first.",
            )
            return
        scope = self._scope()
        default_name = (
            "report_overall.pdf"
            if scope == "overall"
            else f"report_project_{self.project_id or 'current'}.pdf"
        )
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save report PDF",
            default_name,
            "PDF (*.pdf)",
        )
        if not path:
            return
        try:
            export_report_pdf(
                path,
                title=self._report_title,
                subtitle=self._report_subtitle,
                cards=self._report_cards,
                figures=list(self._figures),
            )
        except Exception as exc:
            QMessageBox.critical(self, "Save PDF failed", str(exc))
            return
        QMessageBox.information(self, "Saved", f"Report saved to:\n{path}")

    def _configure_scope(self):
        admin = current_session.is_admin
        self.scope_label.setVisible(admin)
        self.scope_combo.setVisible(admin)
        if not admin:
            idx = self.scope_combo.findData("project")
            if idx >= 0:
                self.scope_combo.blockSignals(True)
                self.scope_combo.setCurrentIndex(idx)
                self.scope_combo.blockSignals(False)
        elif self.project_id is None:
            idx = self.scope_combo.findData("overall")
            if idx >= 0:
                self.scope_combo.blockSignals(True)
                self.scope_combo.setCurrentIndex(idx)
                self.scope_combo.blockSignals(False)

    def _scope(self) -> str:
        if not current_session.is_admin:
            return "project"
        return self.scope_combo.currentData() or "overall"

    def _clear_charts(self):
        while self.charts_layout.count():
            item = self.charts_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.hide()
                widget.setParent(None)
                widget.deleteLater()

        for fig in self._figures:
            try:
                fig.clf()
                from matplotlib import pyplot as plt

                plt.close(fig)
            except Exception:
                pass
        self._figures.clear()

    def refresh(self):
        self._clear_charts()
        self._configure_scope()
        scope = self._scope()

        if scope == "overall":
            self._refresh_overall()
        else:
            self._refresh_project()

    def _refresh_overall(self):
        try:
            stats = portfolio_report_stats(top_n=12)
        except Exception as exc:
            self.subtitle.setText(str(exc))
            return

        outstanding = stats["total_outstanding"]
        net = stats["total_raised"] - stats["total_expenses"]
        subtitle = (
            f"Overall portfolio · {stats['project_count']} project(s) · "
            f"{stats['donor_count']} donor(s) · Net {money(net)} · "
            f"Charts colour-code the top projects by funds raised"
        )
        self.subtitle.setText(subtitle)
        self.card_target.set_value(money(stats["total_target"]), "All project goals")
        self.card_raised.set_value(money(stats["total_raised"]), "Paid across projects")
        self.card_pledged.set_value(money(stats["total_pledged"]), "Committed total")
        self.card_outstanding.set_value(
            money(outstanding), "Still owed by donors"
        )
        self.card_expenses.set_value(money(stats["total_expenses"]), "All project spend")
        self._set_report_snapshot(
            "NGO Fundraising — Overall report",
            subtitle,
            [
                ("TARGET", money(stats["total_target"]), "All project goals"),
                ("RAISED", money(stats["total_raised"]), "Paid across projects"),
                ("PLEDGED", money(stats["total_pledged"]), "Committed total"),
                ("OUTSTANDING", money(outstanding), "Still owed by donors"),
                ("EXPENSES", money(stats["total_expenses"]), "All project spend"),
            ],
        )

        if not _ensure_matplotlib():
            note = QLabel(_charts_unavailable_message())
            note.setObjectName("muted")
            note.setWordWrap(True)
            self.charts_layout.addWidget(note, 0, 0)
            return

        rows = stats["by_project"]
        names = [r["name"] for r in rows]
        colors = [PROJECT_COLORS[i % len(PROJECT_COLORS)] for i in range(len(rows))]
        raised = [float(r["raised"]) for r in rows]
        pledged = [float(r["pledged"]) for r in rows]
        expenses = [float(r["expenses"]) for r in rows]
        outstanding_vals = [float(r["outstanding"]) for r in rows]

        charts = [
            (
                0,
                0,
                self._horizontal_project_chart(
                    "Raised by project", names, raised, colors
                ),
            ),
            (
                0,
                1,
                self._grouped_project_chart(
                    "Pledged · Raised · Outstanding by project",
                    names,
                    pledged,
                    raised,
                    outstanding_vals,
                ),
            ),
            (
                1,
                0,
                self._horizontal_project_chart(
                    "Expenses by project", names, expenses, colors
                ),
            ),
            (
                1,
                1,
                self._multi_line_monthly(
                    "Monthly raised (line graph)",
                    stats["months"],
                    stats["monthly_by_project"],
                ),
            ),
        ]
        for row, col, panel in charts:
            self.charts_layout.addWidget(panel, row, col)
        self.charts_layout.setColumnStretch(0, 1)
        self.charts_layout.setColumnStretch(1, 1)

    def _refresh_project(self):
        if self.project_id is None:
            self.subtitle.setText(
                "Select a project, or switch View to Overall (admin)."
            )
            self.card_target.set_value("0.00")
            self.card_raised.set_value("0.00")
            self.card_pledged.set_value("0.00")
            self.card_outstanding.set_value("0.00")
            self.card_expenses.set_value("0.00")
            self._set_report_snapshot("Reports", self.subtitle.text(), [])
            return

        try:
            stats = project_report_stats(self.project_id)
        except Exception as exc:
            self.subtitle.setText(str(exc))
            return

        project = stats["project"]
        raised = project.amount_raised
        pledged = project.amount_pledged
        expenses = project.total_expenses
        outstanding = pledged - raised
        if outstanding < 0:
            outstanding = Decimal("0.00")
        net = raised - expenses

        subtitle = (
            f"{project.name} · Target {money(project.target_amount)} · "
            f"{project.fundraising_status} · Net {money(net)} · "
            f"Donors {stats['donor_count']} · Donations {stats['donation_count']}"
        )
        self.subtitle.setText(subtitle)
        self.card_target.set_value(money(project.target_amount), "Fundraising goal")
        self.card_raised.set_value(money(raised), "Paid amount")
        self.card_pledged.set_value(money(pledged), "Committed amount")
        self.card_outstanding.set_value(money(outstanding), "Still owed by donors")
        self.card_expenses.set_value(money(expenses), "Project spend")
        self._set_report_snapshot(
            f"NGO Fundraising — Project report · {project.name}",
            subtitle,
            [
                ("TARGET", money(project.target_amount), "Fundraising goal"),
                ("RAISED", money(raised), "Paid amount"),
                ("PLEDGED", money(pledged), "Committed amount"),
                ("OUTSTANDING", money(outstanding), "Still owed by donors"),
                ("EXPENSES", money(expenses), "Project spend"),
            ],
        )

        if not _ensure_matplotlib():
            note = QLabel(
                _charts_unavailable_message(
                    f"Payment methods: {dict(stats['by_method'])}\n"
                    f"Statuses: {stats['by_status']}\n"
                    f"Expense categories: {dict(stats['by_category'])}"
                )
            )
            note.setObjectName("muted")
            note.setWordWrap(True)
            self.charts_layout.addWidget(note, 0, 0)
            return

        monthly = stats["monthly"]
        charts = [
            (
                0,
                0,
                self._bar_chart(
                    "Paid by payment method",
                    list(stats["by_method"].keys()),
                    [float(v) for v in stats["by_method"].values()],
                    "#176B5B",
                ),
            ),
            (
                0,
                1,
                self._bar_chart(
                    "Donations by status",
                    list(stats["by_status"].keys()),
                    [float(v) for v in stats["by_status"].values()],
                    "#2B6CB0",
                ),
            ),
            (
                1,
                0,
                self._line_chart(
                    "Monthly funds raised (line graph)",
                    list(monthly.keys()),
                    [float(v) for v in monthly.values()],
                ),
            ),
            (
                1,
                1,
                self._bar_chart(
                    "Expenses by category",
                    list(stats["by_category"].keys()),
                    [float(v) for v in stats["by_category"].values()],
                    "#C05621",
                ),
            ),
        ]
        for row, col, panel in charts:
            self.charts_layout.addWidget(panel, row, col)
        self.charts_layout.setColumnStretch(0, 1)
        self.charts_layout.setColumnStretch(1, 1)

    def _wrap_canvas(self, canvas: "FigureCanvas") -> QFrame:
        panel = HoverFrame("panel")
        panel.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        box = QVBoxLayout(panel)
        box.setContentsMargins(10, 10, 10, 10)
        canvas.setMinimumHeight(300)
        canvas.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        box.addWidget(canvas)
        return panel

    def _bar_chart(self, title, labels, values, color):
        fig = Figure(figsize=(5.0, 3.4), dpi=100)
        fig.patch.set_facecolor("#FFFFFF")
        ax = fig.add_subplot(111)
        ax.set_facecolor("#FAFBFD")
        canvas = FigureCanvas(fig)
        if labels:
            positions = range(len(labels))
            bars = ax.bar(positions, values, color=color, width=0.55)
            ax.set_xticks(list(positions))
            ax.set_xticklabels(labels, rotation=20, ha="right", fontsize=8)
            enable_bar_hover(canvas, ax, bars, labels=labels)
        else:
            ax.text(0.5, 0.5, "No data", ha="center", va="center")
            ax.set_xticks([])
            ax.set_yticks([])
        ax.set_title(title, fontsize=11, fontweight="bold", color="#17263D")
        ax.tick_params(axis="y", labelsize=8)
        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)
        fig.tight_layout()
        self._figures.append(fig)
        return self._wrap_canvas(canvas)

    def _horizontal_project_chart(self, title, labels, values, colors):
        """Horizontal bars so every project name stays readable."""
        fig = Figure(figsize=(5.4, 4.0), dpi=100)
        fig.patch.set_facecolor("#FFFFFF")
        ax = fig.add_subplot(111)
        ax.set_facecolor("#FAFBFD")
        canvas = FigureCanvas(fig)
        if labels:
            # Draw top project at the top of the chart.
            y = list(range(len(labels)))
            bars = ax.barh(
                y,
                values,
                color=colors,
                height=0.72,
                align="center",
            )
            ax.set_yticks(y)
            ax.set_yticklabels(labels, fontsize=8)
            ax.invert_yaxis()
            ax.tick_params(axis="x", labelsize=8)
            ax.grid(axis="x", color="#E8EEF5", linewidth=0.8)
            enable_bar_hover(
                canvas, ax, bars, labels=labels, horizontal=True
            )
        else:
            ax.text(0.5, 0.5, "No data", ha="center", va="center")
            ax.set_xticks([])
            ax.set_yticks([])
        ax.set_title(title, fontsize=11, fontweight="bold", color="#17263D")
        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)
        fig.tight_layout()
        self._figures.append(fig)
        return self._wrap_canvas(canvas)

    def _grouped_project_chart(self, title, labels, pledged, raised, outstanding):
        fig = Figure(figsize=(5.2, 3.5), dpi=100)
        fig.patch.set_facecolor("#FFFFFF")
        ax = fig.add_subplot(111)
        ax.set_facecolor("#FAFBFD")
        canvas = FigureCanvas(fig)
        if labels:
            import numpy as np

            x = np.arange(len(labels))
            width = 0.26
            b1 = ax.bar(x - width, pledged, width, label="Pledged", color="#6B46C1")
            b2 = ax.bar(x, raised, width, label="Raised", color="#176B5B")
            b3 = ax.bar(
                x + width, outstanding, width, label="Outstanding", color="#C05621"
            )
            ax.set_xticks(list(x))
            ax.set_xticklabels(labels, rotation=28, ha="right", fontsize=7)
            ax.legend(fontsize=8, frameon=False)
            enable_bar_hover(
                canvas,
                ax,
                [b1, b2, b3],
                labels=labels,
                series_names=["Pledged", "Raised", "Outstanding"],
            )
        else:
            ax.text(0.5, 0.5, "No data", ha="center", va="center")
            ax.set_xticks([])
            ax.set_yticks([])
        ax.set_title(title, fontsize=11, fontweight="bold", color="#17263D")
        ax.tick_params(axis="y", labelsize=8)
        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)
        fig.tight_layout()
        self._figures.append(fig)
        return self._wrap_canvas(canvas)

    def _multi_line_monthly(self, title, months, series_map: dict):
        fig = Figure(figsize=(5.2, 3.5), dpi=100)
        fig.patch.set_facecolor("#FFFFFF")
        ax = fig.add_subplot(111)
        ax.set_facecolor("#FAFBFD")
        canvas = FigureCanvas(fig)
        lines = []
        if months and series_map:
            xs = list(range(len(months)))
            totals = [
                sum(float(by_month.get(m, 0)) for by_month in series_map.values())
                for m in months
            ]
            (total_line,) = ax.plot(
                xs,
                totals,
                color="#12233A",
                linewidth=2.4,
                marker="o",
                markersize=4,
                label="All (top projects)",
                zorder=5,
            )
            lines.append(total_line)
            for idx, (name, by_month) in enumerate(series_map.items()):
                ys = [float(by_month.get(m, 0)) for m in months]
                color = PROJECT_COLORS[idx % len(PROJECT_COLORS)]
                (line,) = ax.plot(
                    xs,
                    ys,
                    marker="o",
                    markersize=3.5,
                    linewidth=1.6,
                    label=name,
                    color=color,
                )
                lines.append(line)
            step = max(1, len(months) // 8)
            tick_idx = list(range(0, len(months), step))
            if tick_idx[-1] != len(months) - 1:
                tick_idx.append(len(months) - 1)
            ax.set_xticks(tick_idx)
            ax.set_xticklabels(
                [months[i] for i in tick_idx], rotation=25, ha="right", fontsize=7
            )
            ax.legend(fontsize=6.5, frameon=False, loc="best", ncol=1)
            ax.grid(axis="y", color="#E8EEF5", linewidth=0.8)
            enable_line_hover(canvas, ax, lines, x_labels=months)
        else:
            ax.text(0.5, 0.5, "No monthly data", ha="center", va="center")
            ax.set_xticks([])
            ax.set_yticks([])
        ax.set_title(title, fontsize=11, fontweight="bold", color="#17263D")
        ax.tick_params(axis="y", labelsize=8)
        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)
        fig.tight_layout()
        self._figures.append(fig)
        return self._wrap_canvas(canvas)

    def _line_chart(self, title, labels, values):
        fig = Figure(figsize=(5.0, 3.4), dpi=100)
        fig.patch.set_facecolor("#FFFFFF")
        ax = fig.add_subplot(111)
        ax.set_facecolor("#FAFBFD")
        canvas = FigureCanvas(fig)
        if labels:
            xs = list(range(len(labels)))
            (line,) = ax.plot(
                xs,
                values,
                color="#176B5B",
                marker="o",
                markersize=5,
                linewidth=2.2,
                label="Raised",
            )
            step = max(1, len(labels) // 8)
            tick_idx = list(range(0, len(labels), step))
            if tick_idx[-1] != len(labels) - 1:
                tick_idx.append(len(labels) - 1)
            ax.set_xticks(tick_idx)
            ax.set_xticklabels(
                [labels[i] for i in tick_idx], rotation=25, ha="right", fontsize=8
            )
            ax.grid(axis="y", color="#E8EEF5", linewidth=0.8)
            ax.legend(fontsize=8, frameon=False)
            enable_line_hover(canvas, ax, [line], x_labels=labels)
        else:
            ax.text(0.5, 0.5, "No data", ha="center", va="center")
            ax.set_xticks([])
            ax.set_yticks([])
        ax.set_title(title, fontsize=11, fontweight="bold", color="#17263D")
        ax.tick_params(axis="y", labelsize=8)
        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)
        fig.tight_layout()
        self._figures.append(fig)
        return self._wrap_canvas(canvas)

