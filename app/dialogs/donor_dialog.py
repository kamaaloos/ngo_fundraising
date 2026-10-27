from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QTextEdit,
)


class DonorDialog(QDialog):
    def __init__(self, parent=None, donor=None):
        super().__init__(parent)
        self.setWindowTitle("Donor details")
        self.setMinimumWidth(420)

        layout = QFormLayout(self)
        self.name = QLineEdit()
        self.email = QLineEdit()
        self.phone = QLineEdit()
        self.address = QTextEdit()
        self.address.setMaximumHeight(70)
        self.notes = QTextEdit()
        self.notes.setMaximumHeight(70)

        layout.addRow("Name *", self.name)
        layout.addRow("Email", self.email)
        layout.addRow("Phone", self.phone)
        layout.addRow("Address", self.address)
        layout.addRow("Notes", self.notes)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        if donor:
            self.name.setText(donor.name)
            self.email.setText(donor.email or "")
            self.phone.setText(donor.phone or "")
            self.address.setPlainText(donor.address or "")
            self.notes.setPlainText(donor.notes or "")

    def validate_and_accept(self):
        if not self.name.text().strip():
            QMessageBox.warning(self, "Validation", "Donor name is required.")
            return
        self.accept()

    def values(self):
        return {
            "name": self.name.text().strip(),
            "email": self.email.text().strip(),
            "phone": self.phone.text().strip(),
            "address": self.address.toPlainText().strip(),
            "notes": self.notes.toPlainText().strip(),
        }
