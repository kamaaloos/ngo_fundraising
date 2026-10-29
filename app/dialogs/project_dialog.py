from decimal import Decimal

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QTextEdit,
)

from app.db.models import PROJECT_STATUSES
from app.i18n import td, tr


class ProjectDialog(QDialog):
    def __init__(self, parent=None, project=None):
        super().__init__(parent)
        self.setWindowTitle(tr("dialog.project_title"))
        self.setMinimumWidth(440)

        layout = QFormLayout(self)
        self.name = QLineEdit()
        self.description = QTextEdit()
        self.description.setMaximumHeight(90)
        self.target = QDoubleSpinBox()
        self.target.setRange(0, 1_000_000_000)
        self.target.setDecimals(2)
        self.target.setSingleStep(100)
        self.status = QComboBox()
        for status in PROJECT_STATUSES:
            self.status.addItem(td(status), status)
        self.status.setToolTip(tr("dialog.project.status_tip"))

        layout.addRow(tr("dialog.project.name"), self.name)
        layout.addRow(tr("dialog.project.description"), self.description)
        layout.addRow(tr("dialog.project.target"), self.target)
        layout.addRow(tr("dialog.project.status"), self.status)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Save).setText(tr("common.save"))
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText(
            tr("common.cancel")
        )
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        if project:
            self.name.setText(project.name)
            self.description.setPlainText(project.description or "")
            self.target.setValue(float(project.target_amount))
            status = project.status
            if status == "Completed":
                status = "Archived"
            index = self.status.findData(status)
            self.status.setCurrentIndex(index if index >= 0 else 0)

    def validate_and_accept(self):
        if not self.name.text().strip():
            QMessageBox.warning(
                self, tr("dialog.validation"), tr("dialog.project.err_name")
            )
            return
        if self.target.value() <= 0:
            QMessageBox.warning(
                self, tr("dialog.validation"), tr("dialog.project.err_target")
            )
            return
        self.accept()

    def values(self):
        return {
            "name": self.name.text().strip(),
            "description": self.description.toPlainText().strip(),
            "target_amount": Decimal(str(self.target.value())),
            "status": self.status.currentData() or self.status.currentText(),
        }
