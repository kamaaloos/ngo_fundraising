from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QColor, QTextCharFormat
from PySide6.QtWidgets import QCalendarWidget, QDateEdit, QTableView

CALENDAR_STYLE = """
QCalendarWidget {
    background-color: #FFFFFF;
    border: 1px solid #D5E0EE;
    border-radius: 12px;
}
QCalendarWidget QWidget#qt_calendar_navigationbar {
    background-color: #176B5B;
    border-top-left-radius: 11px;
    border-top-right-radius: 11px;
    min-height: 40px;
}
QCalendarWidget QToolButton {
    color: #FFFFFF;
    background: transparent;
    border: none;
    border-radius: 8px;
    padding: 4px 8px;
    font-size: 13px;
    font-weight: 700;
}
QCalendarWidget QToolButton:hover {
    background-color: rgba(255, 255, 255, 0.18);
}
QCalendarWidget QToolButton#qt_calendar_prevmonth,
QCalendarWidget QToolButton#qt_calendar_nextmonth {
    background-color: rgba(255, 255, 255, 0.16);
    border-radius: 15px;
    width: 30px;
    height: 30px;
    padding: 0;
}
QCalendarWidget QToolButton::menu-indicator {
    image: none;
    width: 0px;
}
QCalendarWidget QSpinBox {
    background-color: rgba(255, 255, 255, 0.16);
    color: #FFFFFF;
    border: 1px solid rgba(255, 255, 255, 0.25);
    border-radius: 8px;
    padding: 2px 6px;
    font-weight: 700;
}
QCalendarWidget QAbstractItemView {
    background-color: #FFFFFF;
    color: #2C3C52;
    selection-background-color: #176B5B;
    selection-color: #FFFFFF;
    outline: 0;
    border: none;
    padding: 0;
    margin: 0;
    font-size: 13px;
    font-weight: 600;
}
QCalendarWidget QAbstractItemView:disabled {
    color: #B0BACA;
}
QCalendarWidget QHeaderView {
    background-color: #F0F7F5;
}
QCalendarWidget QHeaderView::section {
    background-color: #F0F7F5;
    color: #3D7A6C;
    border: none;
    border-bottom: 1px solid #D9E8E3;
    padding: 6px 0;
    font-size: 11px;
    font-weight: 800;
}
"""


def style_calendar(calendar: QCalendarWidget) -> None:
    """Clean calendar that keeps a normal 7-day month grid."""
    calendar.setStyleSheet(CALENDAR_STYLE)
    calendar.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
    calendar.setHorizontalHeaderFormat(
        QCalendarWidget.HorizontalHeaderFormat.ShortDayNames
    )
    calendar.setGridVisible(False)
    calendar.setNavigationBarVisible(True)
    calendar.setFirstDayOfWeek(Qt.DayOfWeek.Monday)
    calendar.setMinimumSize(QSize(320, 280))

    # Reset any inherited table styling that collapses day cells.
    for view in calendar.findChildren(QTableView):
        view.setStyleSheet(
            "QTableView {"
            "  background:#FFFFFF; border:none; outline:0; padding:0; margin:0;"
            "  gridline-color: transparent; alternate-background-color:#FFFFFF;"
            "  selection-background-color:#176B5B; selection-color:#FFFFFF;"
            "}"
            "QTableView::item { padding: 0px; border: none; margin: 0px; }"
            "QHeaderView::section {"
            "  background:#F0F7F5; color:#3D7A6C; border:none;"
            "  border-bottom:1px solid #D9E8E3; padding:6px 0; font-weight:800;"
            "}"
        )
        view.setShowGrid(False)
        view.horizontalHeader().setMinimumSectionSize(36)
        view.verticalHeader().setMinimumSectionSize(28)
        view.verticalHeader().setDefaultSectionSize(32)
        view.horizontalHeader().setDefaultSectionSize(40)

    weekend = QTextCharFormat()
    weekend.setForeground(QColor("#C05621"))
    calendar.setWeekdayTextFormat(Qt.DayOfWeek.Saturday, weekend)
    calendar.setWeekdayTextFormat(Qt.DayOfWeek.Sunday, weekend)

    weekday = QTextCharFormat()
    weekday.setForeground(QColor("#2C3C52"))
    for day in (
        Qt.DayOfWeek.Monday,
        Qt.DayOfWeek.Tuesday,
        Qt.DayOfWeek.Wednesday,
        Qt.DayOfWeek.Thursday,
        Qt.DayOfWeek.Friday,
    ):
        calendar.setWeekdayTextFormat(day, weekday)


def make_date_edit(display_format: str = "yyyy-MM-dd") -> QDateEdit:
    edit = QDateEdit()
    edit.setCalendarPopup(True)
    edit.setDisplayFormat(display_format)
    style_calendar(edit.calendarWidget())
    return edit
