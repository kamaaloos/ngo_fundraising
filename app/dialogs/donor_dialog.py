from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QTextEdit,
)

from app.i18n import tr


class DonorDialog(QDialog):
    def __init__(self, parent=None, donor=None):
        super().__init__(parent)
        self.setWindowTitle(tr("dialog.donor_title"))
        self.setMinimumWidth(420)

        layout = QFormLayout(self)
        self.name = QLineEdit()
        self.email = QLineEdit()
        self.phone = QLineEdit()
        self.address = QTextEdit()
        self.address.setMaximumHeight(70)
        self.notes = QTextEdit()
        self.notes.setMaximumHeight(70)

        layout.addRow(tr("dialog.donor.name"), self.name)
        layout.addRow(tr("dialog.donor.email"), self.email)
        layout.addRow(tr("dialog.donor.phone"), self.phone)
        layout.addRow(tr("dialog.donor.address"), self.address)
        layout.addRow(tr("dialog.donor.notes"), self.notes)

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

        if donor:
            self.name.setText(donor.name)
            self.email.setText(donor.email or "")
            self.phone.setText(donor.phone or "")
            self.address.setPlainText(donor.address or "")
            self.notes.setPlainText(donor.notes or "")

    def validate_and_accept(self):
        if not self.name.text().strip():
            QMessageBox.warning(
                self, tr("dialog.validation"), tr("dialog.donor.err_name")
            )
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
