from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor, QCursor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QTableWidget,
    QTableWidgetItem,
)

HOVER_BG = QColor("#E5F6F1")
HOVER_FG = QColor("#0F5B4B")
ALT_BG = QColor("#F7FAFD")
BASE_BG = QColor("#FFFFFF")
SELECT_BG = QColor("#D5F0E8")
SELECT_FG = QColor("#0F5B4B")


class HoverTableWidget(QTableWidget):
    """Table with full-row hover highlight (not cell-only)."""

    def __init__(self, rows: int = 0, cols: int = 0, parent=None):
        super().__init__(rows, cols, parent)
        self.setObjectName("dataTable")
        self._hover_row = -1
        self.setMouseTracking(True)
        self.viewport().setMouseTracking(True)
        self.setShowGrid(False)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.verticalHeader().setDefaultSectionSize(44)

    def mouseMoveEvent(self, event):
        index = self.indexAt(event.position().toPoint())
        row = index.row() if index.isValid() else -1
        if row != self._hover_row:
            old = self._hover_row
            self._hover_row = row
            self._recolor_row(old)
            self._recolor_row(row)
        super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        old = self._hover_row
        self._hover_row = -1
        self._recolor_row(old)
        super().leaveEvent(event)

    def _recolor_row(self, row: int):
        if row < 0 or row >= self.rowCount():
            return
        selected = {i.row() for i in self.selectedIndexes()}
        for col in range(self.columnCount()):
            item = self.item(row, col)
            if item is None:
                continue
            if row in selected:
                item.setBackground(QBrush(SELECT_BG))
                item.setForeground(QBrush(SELECT_FG))
            elif row == self._hover_row:
                item.setBackground(QBrush(HOVER_BG))
                item.setForeground(QBrush(HOVER_FG))
            else:
                item.setBackground(QBrush(ALT_BG if row % 2 else BASE_BG))
                item.setForeground(QBrush(QColor("#2C3C52")))

    def selectionChanged(self, selected, deselected):
        super().selectionChanged(selected, deselected)
        # Refresh colors for affected rows
        rows = set()
        for idx in selected.indexes():
            rows.add(idx.row())
        for idx in deselected.indexes():
            rows.add(idx.row())
        if self._hover_row >= 0:
            rows.add(self._hover_row)
        for row in rows:
            self._recolor_row(row)


def make_table(headers: list[str]) -> QTableWidget:
    table = HoverTableWidget(0, len(headers))
    table.setHorizontalHeaderLabels(headers)
    table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    table.setAlternatingRowColors(True)
    table.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    table.horizontalHeader().setHighlightSections(False)
    table.verticalHeader().setVisible(False)
    table.setSortingEnabled(False)
    return table


def fill_table(table: QTableWidget, rows: list[tuple]):
    table.setRowCount(len(rows))
    hover_row = getattr(table, "_hover_row", -1)
    for row_index, row in enumerate(rows):
        for col_index, value in enumerate(row):
            item = QTableWidgetItem(str(value))
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            if row_index == hover_row:
                item.setBackground(QBrush(HOVER_BG))
                item.setForeground(QBrush(HOVER_FG))
            else:
                item.setBackground(QBrush(ALT_BG if row_index % 2 else BASE_BG))
            table.setItem(row_index, col_index, item)
    if isinstance(table, HoverTableWidget):
        table._hover_row = -1


def selected_id(table: QTableWidget) -> int | None:
    row = table.currentRow()
    if row < 0:
        return None
    item = table.item(row, 0)
    if item is None:
        return None
    try:
        return int(item.text())
    except ValueError:
        return None
