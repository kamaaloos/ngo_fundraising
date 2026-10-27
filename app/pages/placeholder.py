from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class PlaceholderPage(QWidget):
    def __init__(self, name):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 30, 32, 30)
        title = QLabel(name)
        title.setObjectName('pageTitle')
        layout.addWidget(title)
        note = QLabel(f'{name} module will be implemented in a future phase.')
        note.setObjectName('muted')
        layout.addWidget(note)
        layout.addStretch()
