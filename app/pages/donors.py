from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.auth.session import current_session
from app.db.repository import delete_donor, list_donors, save_donor
from app.dialogs.donor_detail_dialog import DonorDetailDialog
from app.dialogs.donor_dialog import DonorDialog
from app.io.exporters import export_donors_pdf, export_donors_xlsx
from app.io.importers import (
    import_donors_from_file,
    import_donors_linked_to_project,
)
from app.widgets.donor_list_item import DonorListItem


class DonorsPage(QWidget):
    def __init__(self, on_changed=None):
        super().__init__()
        self.on_changed = on_changed
        self.project_id: int | None = None
        self.page = 1
        self.page_size = 10
        self.total = 0
        self._donors = []
        self._selected_id: int | None = None
        self.setObjectName("contentArea")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 26, 28, 26)
        layout.setSpacing(14)

        top = QHBoxLayout()
        title = QLabel("Donors")
        title.setObjectName("pageTitle")
        top.addWidget(title)
        top.addStretch()

        import_btn = QPushButton("Import donors")
        import_btn.setObjectName("ghostButton")
        import_btn.clicked.connect(self.import_donors)
        self.link_import_btn = QPushButton("Import & link to project")
        self.link_import_btn.setObjectName("ghostButton")
        self.link_import_btn.clicked.connect(self.import_linked_to_project)
        export_xls = QPushButton("Export Excel")
        export_xls.setObjectName("ghostButton")
        export_xls.clicked.connect(self.export_excel)
        export_pdf = QPushButton("Export PDF")
        export_pdf.setObjectName("ghostButton")
        export_pdf.clicked.connect(self.export_pdf)
        add = QPushButton("+ Add donor")
        add.setObjectName("primaryButton")
        add.clicked.connect(self.add_donor)
        top.addWidget(import_btn)
        top.addWidget(self.link_import_btn)
        top.addWidget(export_xls)
        top.addWidget(export_pdf)
        top.addWidget(add)
        layout.addLayout(top)
        self.link_import_btn.setEnabled(False)

        note = QLabel(
            "Import donors globally, or Import & link to project to attach them "
            "(with optional pledged/paid) to the open project. "
            "Click a card to select · double-click for details."
        )
        note.setObjectName("muted")
        note.setWordWrap(True)
        layout.addWidget(note)

        filters = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search by name, email, or phone…")
        self.search.textChanged.connect(self._on_search_changed)
        filters.addWidget(self.search, 1)

        filters.addWidget(QLabel("Show"))
        self.scope_combo = QComboBox()
        self.scope_combo.addItem("All donors", "all")
        self.scope_combo.addItem("This project only", "project")
        self.scope_combo.currentIndexChanged.connect(self._reset_and_refresh)
        filters.addWidget(self.scope_combo)
        self._scope_label = filters.itemAt(filters.count() - 2).widget()

        filters.addWidget(QLabel("Per page"))
        self.page_size_combo = QComboBox()
        for size in (5, 10, 25, 50):
            self.page_size_combo.addItem(str(size), size)
        self.page_size_combo.setCurrentIndex(1)
        self.page_size_combo.currentIndexChanged.connect(self._on_page_size_changed)
        filters.addWidget(self.page_size_combo)
        layout.addLayout(filters)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.list_host = QWidget()
        self.list_host.setObjectName("listHost")
        self.list_layout = QVBoxLayout(self.list_host)
        self.list_layout.setContentsMargins(2, 2, 2, 2)
        self.list_layout.setSpacing(10)
        self.list_layout.addStretch()
        self.scroll.setWidget(self.list_host)
        layout.addWidget(self.scroll, 1)

        pager = QHBoxLayout()
        self.prev_btn = QPushButton("‹ Previous")
        self.prev_btn.clicked.connect(self.prev_page)
        self.next_btn = QPushButton("Next ›")
        self.next_btn.clicked.connect(self.next_page)
        self.page_label = QLabel("Page 1")
        self.page_label.setObjectName("muted")
        view = QPushButton("View details")
        view.setObjectName("primaryButton")
        view.clicked.connect(self.view_donor)
        edit = QPushButton("Edit")
        edit.clicked.connect(self.edit_donor)
        self.remove_btn = QPushButton("Delete")
        self.remove_btn.setObjectName("dangerButton")
        self.remove_btn.clicked.connect(self.remove_donor)
        pager.addWidget(self.prev_btn)
        pager.addWidget(self.next_btn)
        pager.addWidget(self.page_label)
        pager.addStretch()
        pager.addWidget(view)
        pager.addWidget(edit)
        pager.addWidget(self.remove_btn)
        layout.addLayout(pager)

        self._search_timer = QTimer(self)
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(280)
        self._search_timer.timeout.connect(self._reset_and_refresh)

    def set_project(self, project_id: int | None):
        self.project_id = project_id
        self.page = 1
        self.link_import_btn.setEnabled(project_id is not None)
        self.refresh()

    def _notify(self):
        if self.on_changed:
            self.on_changed()

    def _on_search_changed(self, *_):
        self._search_timer.start()

    def _on_page_size_changed(self, *_):
        self.page_size = self.page_size_combo.currentData() or 10
        self.page = 1
        self.refresh()

    def _reset_and_refresh(self):
        self.page = 1
        self.refresh()

    def _filter_project_id(self) -> int | None:
        # Non-admins are always scoped in the repository; UI forces project view.
        if not current_session.is_admin:
            return self.project_id
        if self.scope_combo.currentData() == "project":
            return self.project_id
        return None

    def _configure_scope_ui(self):
        admin = current_session.is_admin
        self.scope_combo.setVisible(admin)
        self.remove_btn.setVisible(admin)
        if hasattr(self, "_scope_label") and self._scope_label is not None:
            self._scope_label.setVisible(admin)
        if not admin:
            idx = self.scope_combo.findData("project")
            if idx >= 0:
                self.scope_combo.setCurrentIndex(idx)

    def prev_page(self):
        if self.page > 1:
            self.page -= 1
            self.refresh()

    def next_page(self):
        max_page = max(1, (self.total + self.page_size - 1) // self.page_size)
        if self.page < max_page:
            self.page += 1
            self.refresh()

    def _clear_list(self):
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def refresh(self):
        self._configure_scope_ui()
        if self.project_id is None and (
            not current_session.is_admin
            or self.scope_combo.currentData() == "project"
        ):
            self._clear_list()
            self.list_layout.addStretch()
            self.page_label.setText("Select a project first")
            self.prev_btn.setEnabled(False)
            self.next_btn.setEnabled(False)
            self._donors = []
            return

        donors, total = list_donors(
            search=self.search.text(),
            page=self.page,
            page_size=self.page_size,
            project_id=self._filter_project_id(),
        )
        self.total = total
        max_page = max(1, (total + self.page_size - 1) // self.page_size)
        if self.page > max_page:
            self.page = max_page
            donors, total = list_donors(
                search=self.search.text(),
                page=self.page,
                page_size=self.page_size,
                project_id=self._filter_project_id(),
            )
            self.total = total

        self._donors = donors
        self._clear_list()
        if not donors:
            empty = QLabel("No donors yet. Add one or import from CSV/Excel.")
            empty.setObjectName("muted")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.list_layout.addWidget(empty)
        else:
            for donor in donors:
                item = DonorListItem(donor)
                item.clicked.connect(self._select_donor)
                item.double_clicked.connect(self._open_donor)
                item.payments_clicked.connect(self._open_payments)
                self.list_layout.addWidget(item)
        self.list_layout.addStretch()

        self.page_label.setText(
            f"Page {self.page} of {max_page} · {total} donor(s)"
        )
        self.prev_btn.setEnabled(self.page > 1)
        self.next_btn.setEnabled(self.page < max_page)

    def _select_donor(self, donor_id: int):
        self._selected_id = donor_id

    def _open_donor(self, donor_id: int):
        self._selected_id = donor_id
        self.view_donor()

    def _open_payments(self, donor_id: int):
        from app.dialogs.payment_history_dialog import PaymentHistoryDialog

        self._selected_id = donor_id
        dialog = PaymentHistoryDialog(self, donor_id=donor_id)
        dialog.exec()

    def _current_donor_id(self) -> int | None:
        return self._selected_id

    def view_donor(self, *_):
        donor_id = self._current_donor_id()
        if donor_id is None:
            QMessageBox.information(self, "Select donor", "Click a donor card first.")
            return
        try:
            dialog = DonorDetailDialog(self, donor_id=donor_id)
            dialog.exec()
        except Exception as exc:
            QMessageBox.critical(self, "Could not load donor", str(exc))

    def add_donor(self):
        dialog = DonorDialog(self)
        if dialog.exec():
            try:
                save_donor(None, dialog.values())
                self.refresh()
                self._notify()
            except Exception as exc:
                QMessageBox.critical(self, "Save failed", str(exc))

    def edit_donor(self):
        donor_id = self._current_donor_id()
        if donor_id is None:
            QMessageBox.information(self, "Select donor", "Click a donor card first.")
            return
        from app.db.repository import get_donor

        donor = get_donor(donor_id)
        if donor is None:
            return
        dialog = DonorDialog(self, donor=donor)
        if dialog.exec():
            try:
                save_donor(donor_id, dialog.values())
                self.refresh()
                self._notify()
            except Exception as exc:
                QMessageBox.critical(self, "Save failed", str(exc))

    def remove_donor(self):
        if not current_session.is_admin:
            QMessageBox.information(self, "Permission", "Only admin can delete donors.")
            return
        donor_id = self._current_donor_id()
        if donor_id is None:
            QMessageBox.information(self, "Select donor", "Click a donor card first.")
            return
        if (
            QMessageBox.question(
                self,
                "Confirm deletion",
                "Delete this donor and ALL their donations across every project?",
            )
            != QMessageBox.StandardButton.Yes
        ):
            return
        try:
            delete_donor(donor_id)
            self._selected_id = None
            self.refresh()
            self._notify()
        except Exception as exc:
            QMessageBox.critical(self, "Delete failed", str(exc))

    def _export_donors_dataset(self):
        donors, _total = list_donors(
            search=self.search.text(),
            page=1,
            page_size=10_000,
            project_id=self._filter_project_id(),
        )
        return donors

    def _show_import_result(self, title: str, message: str, warnings: list[str]):
        if warnings:
            preview = "\n".join(warnings[:8])
            more = "" if len(warnings) <= 8 else f"\n… and {len(warnings) - 8} more"
            message += f"\n\nNotes:\n{preview}{more}"
        QMessageBox.information(self, title, message)

    def import_donors(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Import donors",
            "",
            "Spreadsheets (*.csv *.xlsx);;CSV (*.csv);;Excel (*.xlsx)",
        )
        if not path:
            return
        try:
            created, warnings = import_donors_from_file(path)
        except Exception as exc:
            QMessageBox.critical(self, "Import failed", str(exc))
            return
        self._show_import_result(
            "Import complete",
            f"Imported {created} donor(s).",
            warnings,
        )
        self.refresh()
        self._notify()

    def import_linked_to_project(self):
        if self.project_id is None:
            QMessageBox.information(
                self,
                "No project",
                "Open a project first, then import donors linked to it.",
            )
            return
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Import donors linked to this project",
            "",
            "Spreadsheets (*.csv *.xlsx);;CSV (*.csv);;Excel (*.xlsx)",
        )
        if not path:
            return
        try:
            created, reused, donations, warnings = import_donors_linked_to_project(
                path, self.project_id
            )
        except Exception as exc:
            QMessageBox.critical(self, "Import failed", str(exc))
            return
        self._show_import_result(
            "Import complete",
            f"New donors: {created}\n"
            f"Existing donors reused: {reused}\n"
            f"Linked donations: {donations}\n\n"
            "Columns: name, email, phone, pledged, paid, method, date, reference",
            warnings,
        )
        self.refresh()
        self._notify()

    def export_excel(self):
        donors = self._export_donors_dataset()
        if not donors:
            QMessageBox.information(self, "Export", "No donors to export.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Excel",
            "donors.xlsx",
            "Excel (*.xlsx)",
        )
        if not path:
            return
        try:
            export_donors_xlsx(path, donors)
            QMessageBox.information(self, "Export complete", f"Saved:\n{path}")
        except Exception as exc:
            QMessageBox.critical(self, "Export failed", str(exc))

    def export_pdf(self):
        donors = self._export_donors_dataset()
        if not donors:
            QMessageBox.information(self, "Export", "No donors to export.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export PDF",
            "donors.pdf",
            "PDF (*.pdf)",
        )
        if not path:
            return
        try:
            export_donors_pdf(path, donors, title="NGO Fundraising — Donors")
            QMessageBox.information(self, "Export complete", f"Saved:\n{path}")
        except Exception as exc:
            QMessageBox.critical(self, "Export failed", str(exc))
