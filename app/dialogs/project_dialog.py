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


class ProjectDialog(QDialog):
    def __init__(self, parent=None, project=None):
        super().__init__(parent)
        self.setWindowTitle("Project details")
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
        self.status.addItems(list(PROJECT_STATUSES))
        self.status.setToolTip(
            "Set finished campaigns to Archived. They stay in history "
            "but are hidden from the default project list."
        )

        layout.addRow("Project name *", self.name)
        layout.addRow("Description", self.description)
        layout.addRow("Target fund", self.target)
        layout.addRow("Status", self.status)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
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
            index = self.status.findText(status)
            self.status.setCurrentIndex(index if index >= 0 else 0)

    def validate_and_accept(self):
        if not self.name.text().strip():
            QMessageBox.warning(self, "Validation", "Project name is required.")
            return
        if self.target.value() <= 0:
            QMessageBox.warning(self, "Validation", "Target fund must be greater than zero.")
            return
        self.accept()

    def values(self):
        return {
            "name": self.name.text().strip(),
            "description": self.description.toPlainText().strip(),
            "target_amount": Decimal(str(self.target.value())),
            "status": self.status.currentText(),
        }
