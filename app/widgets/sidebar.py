from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app.branding import apply_user_logo, copyright_label, logo_label


class Sidebar(QFrame):
    page_selected = Signal(str)
    logout_requested = Signal()

    def __init__(self):
        super().__init__()
        self.setObjectName("sidebar")
        self.setFixedWidth(248)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 16, 14, 14)
        layout.setSpacing(6)

        # ---- Header (fixed) ----
        self.brand = logo_label(150, 72, object_name="sidebarLogo")
        self.brand.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.brand.setMaximumHeight(78)
        self.brand.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed
        )
        layout.addWidget(self.brand)

        self.user_logo = QLabel()
        self.user_logo.setObjectName("sidebarUserLogo")
        self.user_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.user_logo.setMaximumHeight(52)
        self.user_logo.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed
        )
        self.user_logo.hide()
        layout.addWidget(self.user_logo)
        self.refresh_user_logo()

        self.user_label = QLabel("")
        self.user_label.setObjectName("sidebarCaption")
        self.user_label.setWordWrap(True)
        layout.addWidget(self.user_label)

        self.project_label = QLabel("No project selected")
        self.project_label.setObjectName("sidebarProject")
        self.project_label.setWordWrap(True)
        layout.addWidget(self.project_label)

        # ---- Scrollable nav (never compresses button text) ----
        self.group = QButtonGroup(self)
        self.group.setExclusive(True)
        self._buttons: dict[str, QPushButton] = {}

        nav_host = QWidget()
        nav_host.setObjectName("sidebarNavHost")
        self._nav_layout = QVBoxLayout(nav_host)
        self._nav_layout.setContentsMargins(0, 4, 0, 4)
        self._nav_layout.setSpacing(4)
        self._nav_layout.addStretch(1)

        scroll = QScrollArea()
        scroll.setObjectName("sidebarNavScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setWidget(nav_host)
        scroll.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        layout.addWidget(scroll, 1)

        # ---- Footer (fixed) ----
        logout = QPushButton("Log out")
        logout.setObjectName("navButton")
        logout.setMinimumHeight(40)
        logout.setCursor(Qt.CursorShape.PointingHandCursor)
        logout.clicked.connect(self.logout_requested.emit)
        layout.addWidget(logout)

        layout.addWidget(copyright_label(object_name="sidebarCopyright"))

    def set_user(self, display_name: str, role: str):
        role_label = "ADMIN" if role == "admin" else "USER"
        self.user_label.setText(f"{display_name}\n{role_label}")

    def refresh_user_logo(self):
        apply_user_logo(self.user_logo, 140, 48)

    def set_project_name(self, name: str | None):
        self.project_label.setText(name or "No project selected")

    def set_pages(self, pages: list[tuple[str, str]]):
        """pages: list of (key, label) e.g. ('Dashboard', 'Dashboard')."""
        # Remove stretch then buttons.
        while self._nav_layout.count():
            item = self._nav_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                self.group.removeButton(widget)
                widget.deleteLater()
        self._buttons.clear()

        for i, (key, label) in enumerate(pages):
            button = QPushButton(label)
            button.setObjectName("navButton")
            button.setCheckable(True)
            button.setMinimumHeight(42)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
            )
            button.clicked.connect(
                lambda checked=False, name=key: self.page_selected.emit(name)
            )
            self.group.addButton(button)
            self._nav_layout.addWidget(button)
            self._buttons[key] = button
            if i == 0:
                button.setChecked(True)

        self._nav_layout.addStretch(1)

    def select_page(self, key: str):
        button = self._buttons.get(key)
        if button is not None:
            button.setChecked(True)
