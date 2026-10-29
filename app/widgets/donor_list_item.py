from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout

from app.i18n import tr
from app.utils import money
from app.widgets.avatar import AvatarWidget
from app.widgets.hover_frame import HoverFrame


class DonorListItem(HoverFrame):
    """Modern donor row with avatar placeholder and hover animation."""

    clicked = Signal(int)
    double_clicked = Signal(int)
    payments_clicked = Signal(int)

    def __init__(self, donor, parent=None):
        super().__init__("donorItem", parent)
        self.donor_id = donor.id
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(78)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 12, 16, 12)
        layout.setSpacing(14)

        self.avatar = AvatarWidget(donor.name, size=48)
        layout.addWidget(self.avatar)

        text_col = QVBoxLayout()
        text_col.setSpacing(3)
        name = QLabel(donor.name)
        name.setObjectName("listTitle")
        meta_bits = [b for b in (donor.email or "", donor.phone or "") if b]
        meta = QLabel(
            " · ".join(meta_bits) if meta_bits else tr("donor_item.no_contact")
        )
        meta.setObjectName("listMeta")
        text_col.addWidget(name)
        text_col.addWidget(meta)
        layout.addLayout(text_col, 1)

        stats = QVBoxLayout()
        stats.setSpacing(4)
        stats.setAlignment(Qt.AlignmentFlag.AlignRight)

        amounts = QHBoxLayout()
        amounts.setSpacing(0)
        pledged = QLabel(tr("donor_item.pledged", amount=money(donor.total_pledged)))
        pledged.setObjectName("listMeta")
        paid = QLabel(tr("donor_item.paid", amount=money(donor.total_paid)))
        paid.setObjectName("paidLink")
        paid.setCursor(Qt.CursorShape.PointingHandCursor)
        paid.setToolTip(tr("donor_item.paid_tip"))
        paid.mousePressEvent = self._on_paid_pressed  # type: ignore[method-assign]
        left = QLabel(tr("donor_item.left", amount=money(donor.total_remaining)))
        left.setObjectName("listMeta")
        amounts.addWidget(pledged)
        amounts.addWidget(paid)
        amounts.addWidget(left)
        stats.addLayout(amounts)

        projects = QLabel(
            tr(
                "donor_item.counts",
                projects=len(donor.project_ids),
                donations=len(donor.donations),
            )
        )
        projects.setObjectName("badge")
        projects.setAlignment(Qt.AlignmentFlag.AlignRight)
        stats.addWidget(projects, 0, Qt.AlignmentFlag.AlignRight)
        layout.addLayout(stats)

    def _on_paid_pressed(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.payments_clicked.emit(self.donor_id)
            event.accept()
            return
        event.ignore()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.donor_id)
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.double_clicked.emit(self.donor_id)
        super().mouseDoubleClickEvent(event)
