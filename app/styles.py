STYLESHEET = """
/* ===== Modern fundraising theme ===== */
QWidget {
    font-family: "Segoe UI";
    font-size: 13px;
    color: #1F2A3D;
}

QMainWindow {
    background-color: #E8EEF6;
}

QWidget#contentArea {
    background-color: #E8EEF6;
}

QWidget:focus {
    outline: none;
}

/* ===== Sidebar ===== */
QFrame#sidebar {
    background-color: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 #0B1C2E, stop:1 #12304A
    );
    border: none;
}

QLabel#brand {
    color: #FFFFFF;
    font-size: 21px;
    font-weight: 700;
    padding: 4px 2px;
}

QLabel#sidebarLogo,
QLabel#sidebarUserLogo,
QLabel#loginHeroLogo,
QLabel#loginFormLogo,
QLabel#appLogo {
    background: transparent;
    border: none;
    padding: 0;
}

QLabel#sidebarUserLogo {
    padding: 4px 0 2px 0;
}

QLabel#sidebarCaption {
    color: #8FA3BE;
    font-size: 11px;
    font-weight: 600;
    padding: 6px 8px;
}

QLabel#sidebarCopyright {
    color: #6B8199;
    font-size: 9px;
    font-weight: 500;
    padding: 4px 4px 0 4px;
}

QLabel#loginCopyright {
    color: #6B7A90;
    font-size: 11px;
    font-weight: 500;
}

QLabel#statusCopyright {
    color: #6B7A90;
    font-size: 11px;
    padding-right: 8px;
}

QLabel#sidebarProject {
    color: #E7F7F2;
    font-size: 12px;
    font-weight: 600;
    background-color: rgba(23, 107, 91, 0.35);
    border: 1px solid rgba(94, 191, 168, 0.35);
    border-radius: 10px;
    padding: 10px 12px;
}

QScrollArea#sidebarNavScroll {
    background: transparent;
    border: none;
}

QScrollArea#sidebarNavScroll > QWidget > QWidget {
    background: transparent;
}

QWidget#sidebarNavHost {
    background: transparent;
}

QPushButton#navButton {
    background-color: transparent;
    color: #B9C7DA;
    border: none;
    border-radius: 11px;
    text-align: left;
    padding: 10px 12px;
    margin: 1px 0;
    font-size: 13px;
    font-weight: 500;
    min-height: 42px;
}

QPushButton#navButton:hover {
    background-color: rgba(255, 255, 255, 0.08);
    color: #FFFFFF;
}

QPushButton#navButton:checked {
    background-color: #176B5B;
    color: #FFFFFF;
    font-weight: 600;
}

QPushButton#navButton:pressed {
    background-color: #105546;
}

/* ===== Page headings ===== */
QLabel#pageTitle {
    color: #12233A;
    font-size: 27px;
    font-weight: 700;
    padding: 2px 0;
}

QLabel#muted {
    color: #6B7A90;
    font-size: 12px;
}

QLabel#sectionTitle {
    color: #12233A;
    font-size: 16px;
    font-weight: 700;
}

QLabel#badge {
    background-color: #DDF3EC;
    color: #0F5B4B;
    border-radius: 7px;
    padding: 4px 10px;
    font-size: 11px;
    font-weight: 700;
}

QLabel#avatarLabel {
    color: #FFFFFF;
    font-size: 15px;
    font-weight: 700;
}

QLabel#listTitle {
    color: #12233A;
    font-size: 15px;
    font-weight: 700;
}

QLabel#listMeta {
    color: #6B7A90;
    font-size: 12px;
}

QLabel#paidLink {
    color: #176B5B;
    font-size: 12px;
    font-weight: 700;
    text-decoration: underline;
}

QLabel#paidLink:hover {
    color: #0F5B4B;
}

/* ===== Cards / panels ===== */
QFrame#card {
    background-color: #FFFFFF;
    border: 1px solid #D9E3F0;
    border-radius: 16px;
}

QFrame#cardAccentTeal {
    background-color: #FFFFFF;
    border: 1px solid #C9E7DE;
    border-left: 5px solid #176B5B;
    border-radius: 16px;
}

QFrame#cardAccentBlue {
    background-color: #FFFFFF;
    border: 1px solid #D0DFF3;
    border-left: 5px solid #2B6CB0;
    border-radius: 16px;
}

QFrame#cardAccentAmber {
    background-color: #FFFFFF;
    border: 1px solid #F0E0C8;
    border-left: 5px solid #C05621;
    border-radius: 16px;
}

QFrame#cardAccentRose {
    background-color: #FFFFFF;
    border: 1px solid #F0D4D4;
    border-left: 5px solid #C53030;
    border-radius: 16px;
}

QFrame#cardAccentViolet {
    background-color: #FFFFFF;
    border: 1px solid #DDD6F3;
    border-left: 5px solid #6B46C1;
    border-radius: 16px;
}

QFrame#panel {
    background-color: #FFFFFF;
    border: 1px solid #D9E3F0;
    border-radius: 16px;
}

QFrame#donorItem {
    background-color: #FFFFFF;
    border: 1px solid #D5E0EE;
    border-radius: 14px;
}

QFrame#donorItem:hover {
    background-color: #E5F6F1;
    border: 1px solid #9FD2C3;
}

QFrame#donorItem:hover QLabel#listTitle {
    color: #0F5B4B;
}

QFrame#donorItem:hover QLabel#listMeta {
    color: #3D7A6C;
}

QFrame#listHost {
    background-color: transparent;
    border: none;
}

QLabel#cardTitle {
    color: #6B7A90;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.5px;
}

QLabel#cardValue {
    color: #12233A;
    font-size: 26px;
    font-weight: 700;
}

/* ===== Progress ===== */
QProgressBar {
    background-color: #DCE5F0;
    border: none;
    border-radius: 6px;
    height: 10px;
    text-align: center;
    color: transparent;
}

QProgressBar::chunk {
    background-color: #176B5B;
    border-radius: 6px;
}

/* ===== Buttons ===== */
QPushButton {
    background-color: #FFFFFF;
    color: #2C3C52;
    border: 1px solid #CDD8E6;
    border-radius: 9px;
    padding: 9px 14px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #F2F7FC;
    border-color: #A9BBD0;
}

QPushButton:pressed {
    background-color: #E5EDF6;
}

QPushButton:disabled {
    background-color: #F1F3F6;
    color: #A0AAB8;
    border-color: #E3E7ED;
}

QPushButton#primaryButton {
    background-color: #176B5B;
    color: #FFFFFF;
    border: 1px solid #176B5B;
    border-radius: 9px;
    padding: 10px 18px;
    font-weight: 600;
}

QPushButton#primaryButton:hover {
    background-color: #125747;
    border-color: #125747;
}

QPushButton#primaryButton:pressed {
    background-color: #0E493D;
}

QPushButton#ghostButton {
    background-color: #EAF4F1;
    color: #125747;
    border: 1px solid #C5E4DA;
}

QPushButton#ghostButton:hover {
    background-color: #D8EFE8;
    border-color: #9FD2C3;
}

QPushButton#dangerButton {
    background-color: #FFFFFF;
    color: #B42318;
    border: 1px solid #F3C4C0;
}

QPushButton#dangerButton:hover {
    background-color: #FEF3F2;
    border-color: #F09790;
}

/* ===== Forms ===== */
QLineEdit,
QTextEdit,
QPlainTextEdit,
QDateEdit,
QDateTimeEdit,
QDoubleSpinBox,
QSpinBox,
QComboBox {
    background-color: #FFFFFF;
    color: #1F2A3D;
    border: 1px solid #CDD8E6;
    border-radius: 9px;
    padding: 8px 10px;
    selection-background-color: #D7EEE8;
    selection-color: #173F37;
}

QLineEdit:hover,
QTextEdit:hover,
QPlainTextEdit:hover,
QDateEdit:hover,
QDateTimeEdit:hover,
QDoubleSpinBox:hover,
QSpinBox:hover,
QComboBox:hover {
    border-color: #A8B9CB;
}

QLineEdit:focus,
QTextEdit:focus,
QPlainTextEdit:focus,
QDateEdit:focus,
QDateTimeEdit:focus,
QDoubleSpinBox:focus,
QSpinBox:focus,
QComboBox:focus {
    border: 1px solid #16836C;
}

QDateEdit::drop-down,
QDateTimeEdit::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: center right;
    width: 28px;
    border: none;
    background: transparent;
}

/* Calendar chrome is applied per-widget in app.widgets.date_edit
   so global QTableView rules cannot break the day grid. */

QComboBox::drop-down {
    border: none;
    width: 26px;
}

QComboBox QAbstractItemView {
    background-color: #FFFFFF;
    color: #1F2A3D;
    border: 1px solid #CDD8E6;
    selection-background-color: #E3F3EF;
    selection-color: #145748;
    padding: 4px;
}

QCheckBox {
    spacing: 8px;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 1px solid #C5D0DE;
    background: #FFFFFF;
}

QCheckBox::indicator:checked {
    background: #176B5B;
    border-color: #176B5B;
}

/* ===== Tables / list views (scoped — do not style calendar QTableView) ===== */
QTableWidget#dataTable {
    background-color: #FFFFFF;
    alternate-background-color: #F7FAFD;
    color: #2C3C52;
    border: 1px solid #D5E0EE;
    border-radius: 16px;
    gridline-color: transparent;
    selection-background-color: #D5F0E8;
    selection-color: #0F5B4B;
    outline: none;
    padding: 4px;
}

QTableWidget#dataTable::item {
    padding: 10px 12px;
    border: none;
    border-bottom: 1px solid #EEF2F7;
}

QTableWidget#dataTable::item:selected {
    background-color: #D5F0E8;
    color: #0F5B4B;
}

QTableWidget#dataTable::item:hover {
    background-color: #E5F6F1;
    color: #0F5B4B;
}

QTableWidget#dataTable QHeaderView::section {
    background-color: #F0F5FB;
    color: #5A6B82;
    border: none;
    border-bottom: 1px solid #D5E0EE;
    padding: 13px 12px;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0.3px;
}

QTableWidget#dataTable QHeaderView::section:hover {
    background-color: #E7EEF7;
    color: #176B5B;
}

QTableWidget#dataTable QTableCornerButton::section {
    background-color: #F0F5FB;
    border: none;
}

/* ===== Login split cinematic ===== */
QDialog#loginDialog {
    background-color: #E8EEF6;
}

QWidget#loginRightPane {
    background-color: #E8EEF6;
}

QWidget#loginHero {
    background-color: #12304A;
}

QLabel#loginHeroBrand {
    color: #FFFFFF;
    font-size: 34px;
    font-weight: 800;
}

QLabel#loginHeroTagline {
    color: #FFFFFF;
    font-size: 28px;
    font-weight: 750;
    line-height: 1.22;
}

QLabel#loginHeroCaption {
    color: rgba(255, 255, 255, 0.82);
    font-size: 15px;
    font-weight: 500;
    padding-top: 10px;
}

QLabel#loginHeroCopyright {
    color: rgba(255, 255, 255, 0.62);
    font-size: 11px;
    font-weight: 500;
    background: transparent;
    padding-top: 12px;
}

QFrame#loginFormCard {
    background-color: #FFFFFF;
    border: 1.5px solid #176B5B;
    border-radius: 18px;
}

QFrame#loginFormCard[raised="true"] {
    border: 2px solid #125747;
    background-color: #FBFFFE;
}

QLabel#loginEyebrow {
    color: #176B5B;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1.2px;
}

QScrollArea#loginFormScroll {
    background-color: #E8EEF6;
    border: none;
}

QScrollArea#loginFormScroll > QWidget > QWidget {
    background-color: #E8EEF6;
}

QScrollArea#settingsScroll {
    background-color: #E8EEF6;
    border: none;
}

QScrollArea#settingsScroll > QWidget > QWidget {
    background-color: #E8EEF6;
}

QLabel#loginTitle {
    color: #12233A;
    font-size: 24px;
    font-weight: 800;
}

QLabel#loginSubtitle {
    color: #6B7A90;
    font-size: 13px;
}

QLabel#loginFieldLabel {
    color: #35455C;
    font-size: 12px;
    font-weight: 700;
}

QLabel#loginHint {
    color: #176B5B;
    font-size: 11px;
    font-weight: 600;
    background-color: #E3F3EF;
    border-radius: 8px;
    padding: 8px 12px;
}

QPushButton#loginForgotLink {
    background: transparent;
    border: none;
    color: #176B5B;
    font-size: 12px;
    font-weight: 600;
    text-decoration: underline;
    padding: 4px;
}

QPushButton#loginForgotLink:hover {
    color: #0E493D;
}

QWidget#languageSwitch {
    background: transparent;
}

QPushButton#langSwitchBtn {
    background-color: #EEF3F9;
    color: #35455C;
    border: 1px solid #C5D0DE;
    border-radius: 8px;
    font-size: 12px;
    font-weight: 700;
    padding: 6px 12px;
    min-width: 44px;
}

QPushButton#langSwitchBtn:hover {
    border-color: #176B5B;
    color: #145748;
}

QPushButton#langSwitchBtn:checked {
    background-color: #176B5B;
    color: #FFFFFF;
    border-color: #176B5B;
}

QLabel#loginInstallId {
    color: #6B7A90;
    font-size: 11px;
    font-weight: 600;
}

QWidget#loginInputShell {
    background-color: #FFFFFF;
    border: 1.5px solid #C9D6E5;
    border-radius: 12px;
    min-height: 44px;
    margin-top: 2px;
    margin-bottom: 0px;
}

QWidget#loginInputShell[hovered="true"],
QWidget#loginInputShell[focused="true"] {
    border: 1.5px solid #176B5B;
    background-color: #F4FBF8;
    margin-top: 0px;
    margin-bottom: 4px;
}

QLabel#loginFieldIcon {
    color: #176B5B;
    font-size: 16px;
    background: transparent;
    border: none;
}

QPushButton#loginEyeButton {
    background: transparent;
    border: none;
    color: #5E6E84;
    font-size: 15px;
    border-radius: 8px;
    padding: 4px;
}

QPushButton#loginEyeButton:hover {
    background-color: #E3F3EF;
    color: #176B5B;
    border: none;
}

QLineEdit#loginInput {
    background: transparent;
    border: none;
    padding: 6px 2px;
    font-size: 14px;
    color: #12233A;
}

QLineEdit#loginInput:focus {
    border: none;
    background: transparent;
}

QPushButton#infoIconButton {
    background-color: #E3F3EF;
    color: #176B5B;
    border: 1px solid #B7D9CF;
    border-radius: 10px;
    font-size: 11px;
    font-weight: 800;
    padding: 0;
    min-width: 20px;
    max-width: 20px;
    min-height: 20px;
    max-height: 20px;
}

QPushButton#infoIconButton:hover {
    background-color: #176B5B;
    color: #FFFFFF;
    border-color: #176B5B;
}

QPushButton#loginPrimary {
    background-color: #176B5B;
    color: #FFFFFF;
    border: none;
    border-radius: 12px;
    font-size: 15px;
    font-weight: 700;
    padding: 12px 18px;
}

QPushButton#loginPrimary:hover {
    background-color: #125747;
}

QPushButton#loginPrimary:pressed {
    background-color: #0E493D;
}

/* ===== Scrollbars ===== */
QScrollBar:vertical {
    background-color: transparent;
    width: 10px;
    margin: 2px;
}

QScrollBar::handle:vertical {
    background-color: #C5D0DE;
    border-radius: 5px;
    min-height: 25px;
}

QScrollBar::handle:vertical:hover {
    background-color: #96A8BD;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {
    background: none;
    border: none;
    height: 0;
}

/* ===== Dialogs ===== */
QDialog {
    background-color: #E8EEF6;
}

QMessageBox {
    background-color: #FFFFFF;
}

QStatusBar {
    background-color: #FFFFFF;
    color: #6B7A90;
    border-top: 1px solid #D9E3F0;
}

QToolTip {
    background-color: #12233A;
    color: #FFFFFF;
    border: none;
    padding: 6px 8px;
    border-radius: 4px;
}
"""


def build_stylesheet(settings=None) -> str:
    """Build CSS from the base theme using saved accent + day/night mode."""
    from app.settings_store import THEME_PRESETS, load_settings

    settings = settings or load_settings()
    accent = THEME_PRESETS[settings.accent_key()]
    css = STYLESHEET

    # Accent swaps (base stylesheet is teal).
    for old, new in (
        ("#176B5B", accent["accent"]),
        ("#125747", accent["accent_hover"]),
        ("#0E493D", accent["accent_pressed"]),
        ("#105546", accent["accent_pressed"]),
        ("#E3F3EF", accent["accent_soft"]),
        ("#EAF4F1", accent["accent_soft"]),
        ("#D8EFE8", accent["accent_soft"]),
        ("#DDF3EC", accent["accent_soft"]),
        ("#E5F6F1", accent["accent_soft"]),
        ("#D5F0E8", accent["accent_soft"]),
        ("#D7EEE8", accent["accent_soft"]),
        ("#FBFFFE", accent["accent_soft"]),
        ("#F4FBF8", accent["accent_soft"]),
        ("rgba(23, 107, 91, 0.35)", _hex_to_rgba(accent["accent"], 0.35)),
        ("rgba(94, 191, 168, 0.35)", _hex_to_rgba(accent["accent_soft_border"], 0.45)),
    ):
        css = css.replace(old, new)

    if settings.mode_key() == "night":
        css += _night_mode_overrides(accent)

    return css


def _night_mode_overrides(accent: dict) -> str:
    """High-contrast night theme. Avoid global #FFFFFF remaps (they kill white text)."""
    a = accent["accent"]
    a_hover = accent["accent_hover"]
    a_pressed = accent["accent_pressed"]
    a_soft = accent["accent_soft"]
    sidebar_top = _shade(a_pressed, 0.35)
    sidebar_bot = _shade(a_hover, 0.55)
    return f"""

/* ===== Night mode overrides (high contrast) ===== */
QWidget {{
    color: #F1F5F9;
}}

QMainWindow,
QWidget#contentArea {{
    background-color: #0B1220;
}}

QScrollArea#settingsScroll,
QScrollArea#settingsScroll > QWidget > QWidget {{
    background-color: #0B1220;
}}

QFrame#sidebar {{
    background-color: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 {sidebar_top}, stop:1 {sidebar_bot}
    );
}}

QLabel#brand,
QLabel#sidebarCaption,
QLabel#sidebarCopyright {{
    color: #E2E8F0;
}}

QLabel#sidebarCaption {{
    color: #CBD5E1;
}}

QLabel#sidebarCopyright {{
    color: #94A3B8;
}}

QLabel#sidebarProject {{
    color: #F8FAFC;
    background-color: {_hex_to_rgba(a, 0.45)};
    border: 1px solid {_hex_to_rgba("#FFFFFF", 0.28)};
}}

QPushButton#navButton {{
    color: #E2E8F0;
}}

QPushButton#navButton:hover {{
    background-color: rgba(255, 255, 255, 0.14);
    color: #FFFFFF;
}}

QPushButton#navButton:checked {{
    background-color: {a};
    color: #FFFFFF;
}}

QPushButton#navButton:pressed {{
    background-color: {a_pressed};
    color: #FFFFFF;
}}

QStatusBar {{
    background-color: {sidebar_bot};
    color: #F1F5F9;
    border-top: 1px solid {_hex_to_rgba("#FFFFFF", 0.12)};
}}

QStatusBar QLabel,
QLabel#statusCopyright,
QPushButton#loginForgotLink {{
    color: #E2E8F0;
    background: transparent;
}}

QPushButton#langSwitchBtn {{
    background-color: #1E2D45;
    color: #E2E8F0;
    border: 1px solid #475569;
}}

QPushButton#langSwitchBtn:hover {{
    border-color: {a};
    color: #FFFFFF;
}}

QPushButton#langSwitchBtn:checked {{
    background-color: {a};
    color: #FFFFFF;
    border-color: {a};
}}

QLabel#pageTitle,
QLabel#sectionTitle,
QLabel#cardTitle,
QLabel#cardValue,
QLabel#loginTitle {{
    color: #F8FAFC;
}}

QLabel#muted,
QLabel#loginSubtitle,
QLabel#loginCopyright {{
    color: #CBD5E1;
}}

QFrame#panel,
QFrame#loginFormCard,
QFrame#cardAccentTeal,
QFrame#cardAccentBlue,
QFrame#cardAccentAmber,
QFrame#cardAccentRose,
QFrame#cardAccentViolet {{
    background-color: #162033;
    color: #F1F5F9;
}}

QFrame#panel,
QFrame#loginFormCard {{
    border: 1px solid #334155;
}}

QFrame#cardAccentTeal,
QFrame#cardAccentBlue,
QFrame#cardAccentAmber,
QFrame#cardAccentRose,
QFrame#cardAccentViolet {{
    border: 1px solid #334155;
}}

QLabel#cardTitle {{
    color: #94A3B8;
}}

QLabel#cardValue {{
    color: #F8FAFC;
}}

QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QSpinBox, QDoubleSpinBox,
QDateEdit, QDateTimeEdit {{
    background-color: #0F1A2A;
    color: #F8FAFC;
    border: 1px solid #475569;
    selection-background-color: {a};
    selection-color: #FFFFFF;
}}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus,
QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus {{
    border: 1px solid {a};
}}

QComboBox QAbstractItemView {{
    background-color: #162033;
    color: #F8FAFC;
    selection-background-color: {a};
    selection-color: #FFFFFF;
}}

QTableWidget#dataTable,
QTableView {{
    background-color: #101A2B;
    alternate-background-color: #162033;
    color: #F1F5F9;
    gridline-color: #334155;
    selection-background-color: {_hex_to_rgba(a, 0.45)};
    selection-color: #FFFFFF;
}}

QHeaderView::section {{
    background-color: #1E2D45;
    color: #F8FAFC;
    border: none;
    border-bottom: 1px solid #334155;
    padding: 8px;
}}

QPushButton {{
    color: #F8FAFC;
}}

QPushButton#primaryButton,
QPushButton#loginPrimary {{
    background-color: {a};
    color: #FFFFFF;
    border: 1px solid {a};
}}

QPushButton#primaryButton:hover,
QPushButton#loginPrimary:hover {{
    background-color: {a_hover};
    color: #FFFFFF;
}}

QPushButton#ghostButton {{
    background-color: transparent;
    color: #E2E8F0;
    border: 1px solid #64748B;
}}

QPushButton#ghostButton:hover {{
    background-color: {_hex_to_rgba("#FFFFFF", 0.08)};
    color: #FFFFFF;
}}

QMessageBox {{
    background-color: #162033;
    color: #F1F5F9;
}}

QMessageBox QLabel {{
    color: #F1F5F9;
}}

QToolTip {{
    background-color: #0B1220;
    color: #F8FAFC;
    border: 1px solid #475569;
}}

QScrollBar::handle:vertical {{
    background: #475569;
}}

QScrollBar::handle:vertical:hover {{
    background: {a};
}}

QRadioButton, QCheckBox {{
    color: #F1F5F9;
}}

QLabel#badge {{
    color: {a_soft};
}}
"""


def _hex_to_rgba(hex_color: str, alpha: float) -> str:
    value = hex_color.lstrip("#")
    if len(value) != 6:
        return hex_color
    r = int(value[0:2], 16)
    g = int(value[2:4], 16)
    b = int(value[4:6], 16)
    return f"rgba({r}, {g}, {b}, {alpha})"


def _shade(hex_color: str, factor: float) -> str:
    """Darken (factor < 1) a hex color toward black."""
    value = hex_color.lstrip("#")
    if len(value) != 6:
        return hex_color
    r = int(int(value[0:2], 16) * factor)
    g = int(int(value[2:4], 16) * factor)
    b = int(int(value[4:6], 16) * factor)
    return f"#{max(0, min(255, r)):02X}{max(0, min(255, g)):02X}{max(0, min(255, b)):02X}"
