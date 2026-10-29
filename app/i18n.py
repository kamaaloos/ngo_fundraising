"""App UI language (English, Arabic, Somali).

Use ``tr("key")`` for user-visible strings. Language is stored in UI settings
and applied at startup (layout direction + string catalog).

Use ``td(value)`` for known domain values (project status, payment method,
yes/no, roles, fundraising status) stored in English in the database.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

LANG_EN = "en"
LANG_AR = "ar"
LANG_SO = "so"

LANGUAGE_OPTIONS = (
    (LANG_EN, "English"),
    (LANG_AR, "العربية"),
    (LANG_SO, "Soomaali"),
)

_current = LANG_EN

# English domain value (lowered) -> catalog key
_DOMAIN_KEYS: dict[str, str] = {
    "active": "domain.active",
    "completed": "domain.completed",
    "on hold": "domain.on_hold",
    "archived": "domain.archived",
    "cash": "domain.cash",
    "bank transfer": "domain.bank_transfer",
    "mobile money": "domain.mobile_money",
    "cheque": "domain.cheque",
    "check": "domain.cheque",
    "other": "domain.other",
    "card": "domain.card",
    "online": "domain.online",
    "yes": "common.yes",
    "no": "common.no",
    "admin": "domain.admin",
    "user": "domain.user",
    "pending": "domain.pending",
    "remaining": "domain.remaining",
    "not started": "domain.not_started",
    "in progress": "domain.in_progress",
    "fully funded": "domain.fully_funded",
}

_STRINGS: dict[str, dict[str, str]] = {
    LANG_EN: {
        "app.name": "NGO Fundraising",
        "nav.overview": "Overview",
        "nav.projects": "Projects",
        "nav.dashboard": "Project board",
        "nav.donors": "Donors",
        "nav.donations": "Donations",
        "nav.expenses": "Expenses",
        "nav.reports": "Reports",
        "nav.users": "Users",
        "nav.settings": "Settings",
        "nav.logout": "Log out",
        "nav.no_project": "No project selected",
        "role.admin": "ADMIN",
        "role.user": "USER",
        "common.save": "Save",
        "common.cancel": "Cancel",
        "common.delete": "Delete",
        "common.edit": "Edit",
        "common.add": "Add",
        "common.close": "Close",
        "common.yes": "Yes",
        "common.no": "No",
        "common.ready": "Ready",
        "common.refresh": "Refresh",
        "common.search": "Search",
        "common.import": "Import",
        "common.export": "Export",
        "common.open": "Open",
        "common.previous": "‹ Previous",
        "common.next": "Next ›",
        "common.select_first": "Select an item first.",
        "common.no_project_title": "No project",
        "common.no_project_body": "Open a project first.",
        "common.confirm_delete": "Confirm deletion",
        "common.save_failed": "Save failed",
        "common.delete_failed": "Delete failed",
        "common.permission": "Permission",
        "common.all": "All",
        "col.id": "ID",
        "col.date": "Date",
        "col.donor": "Donor",
        "col.project": "Project",
        "col.status": "Status",
        "col.target": "Target",
        "col.pledged": "Pledged",
        "col.raised": "Raised",
        "col.outstanding": "Outstanding",
        "col.paid": "Paid",
        "col.remaining": "Remaining",
        "col.method": "Method",
        "col.reference": "Reference",
        "col.fund_status": "Fund status",
        "col.progress": "Progress",
        "col.name": "Name",
        "col.expenses": "Expenses",
        "col.title": "Title",
        "col.category": "Category",
        "col.amount": "Amount",
        "col.notes": "Notes",
        "col.collected_by": "Collected by",
        "col.username": "Username",
        "col.full_name": "Full name",
        "col.role": "Role",
        "col.active": "Active",
        "col.projects": "Projects",
        "card.projects": "PROJECTS",
        "card.pledged": "PLEDGED",
        "card.raised": "RAISED",
        "card.outstanding": "OUTSTANDING",
        "card.expenses": "EXPENSES",
        "card.target": "TARGET",
        "card.projects_hint": "Accessible to you",
        "card.pledged_hint": "Committed by donors",
        "card.raised_hint": "Already paid",
        "card.outstanding_hint": "Still owed by donors",
        "card.outstanding_hint_detail": "Pledged − raised (donors still owe)",
        "card.expenses_hint": "Recorded spend",
        "card.target_hint": "Fundraising goal",
        "card.raised_paid_hint": "Paid amount",
        "card.pledged_committed_hint": "Committed amount",
        "card.outstanding_owed_hint": "Still owed by donors",
        "card.expenses_project_hint": "Project spend",
        "domain.active": "Active",
        "domain.completed": "Completed",
        "domain.on_hold": "On hold",
        "domain.archived": "Archived",
        "domain.cash": "Cash",
        "domain.bank_transfer": "Bank transfer",
        "domain.mobile_money": "Mobile money",
        "domain.cheque": "Cheque",
        "domain.other": "Other",
        "domain.card": "Card",
        "domain.online": "Online",
        "domain.admin": "admin",
        "domain.user": "user",
        "domain.pending": "Pending",
        "domain.remaining": "Remaining",
        "domain.not_started": "Not started",
        "domain.in_progress": "In progress",
        "domain.fully_funded": "Fully funded",
        "login.title": "Sign in — NGO Fundraising",
        "login.eyebrow": "SECURE ACCESS",
        "login.welcome": "Welcome back",
        "login.subtitle": "Sign in to manage Islamic fundraising projects, donors, and reports.",
        "login.username": "Username",
        "login.password": "Password",
        "login.username_ph": "Enter your username",
        "login.password_ph": "Enter your password",
        "login.sign_in": "Sign in",
        "login.forgot": "Forgot admin password? Contact support",
        "login.hint": "First launch creates admin — you will be asked to change the password.",
        "login.failed": "Sign in failed",
        "login.failed_body": "Invalid credentials or inactive account.",
        "login.license": "Enter / renew license code",
        "login.empty": "Enter username and password.",
        "settings.title": "Settings",
        "settings.note": (
            "Personalize this computer’s look. Your organization logo appears in "
            "the sidebar — the MayleSoft app icon stays unchanged."
        ),
        "settings.language": "Language",
        "settings.language_hint": (
            "English, Arabic, or Somali for the app interface. "
            "Arabic uses right-to-left layout."
        ),
        "settings.language_restart": (
            "Language saved. The app will restart so menus and screens update fully."
        ),
        "settings.theme": "Theme color",
        "settings.theme_hint": "Accent color for buttons, highlights, and navigation.",
        "settings.mode": "Display mode",
        "settings.mode_hint": "Day keeps a light workspace; Night uses a dark workspace.",
        "settings.mode.day": "Day (light)",
        "settings.mode.night": "Night (dark)",
        "settings.logo": "Organization logo",
        "settings.logo_hint": (
            "Shown in the sidebar under your session. This is your logo — "
            "not the NGO Fundraising app icon."
        ),
        "settings.logo_none": "No organization logo",
        "settings.logo_choose": "Choose logo…",
        "settings.logo_remove": "Remove logo",
        "settings.backup": "Data backup",
        "settings.backup_hint": (
            "This install stores data on this PC only — there is no shared multi-PC "
            "database in this version. Export a copy regularly, or restore from a "
            "backup file (restore replaces current data and requires a restart)."
        ),
        "settings.backup_on_exit": "Write a local backup when quitting the app",
        "settings.export_backup": "Export backup…",
        "settings.restore_backup": "Restore from backup…",
        "settings.about": "About",
        "settings.product": "Product",
        "settings.support_email": "Support email",
        "settings.install_id": "Install ID",
        "overview.title": "Overview",
        "overview.subtitle": "Your fundraising portfolio",
        "overview.projects": "Projects",
        "overview.open_dashboard": "Open project dashboard",
        "overview.role_admin": "Administrator",
        "overview.role_user": "Project user",
        "overview.signed_in": (
            "Signed in as {name} · {role} · {donors} donor(s) · "
            "Outstanding (donors still owe): {outstanding} · "
            "Cash net (raised − expenses): {net}"
        ),
        "donors.title": "Donors",
        "donors.import": "Import donors",
        "donors.import_link": "Import & link to project",
        "donors.export_excel": "Export Excel",
        "donors.export_pdf": "Export PDF",
        "donors.add": "+ Add donor",
        "donors.note": (
            "Import donors globally, or Import & link to project to attach them "
            "(with optional pledged/paid) to the open project. "
            "Click a card to select · double-click for details."
        ),
        "donors.search_ph": "Search by name, email, or phone…",
        "donors.show": "Show",
        "donors.all": "All donors",
        "donors.this_project": "This project only",
        "donors.per_page": "Per page",
        "donors.empty": "No donors yet. Add one or import from CSV/Excel.",
        "donors.page": "Page {page} of {max_page} · {total} donor(s)",
        "donors.select_title": "Select donor",
        "donors.select_body": "Click a donor card first.",
        "donors.view_details": "View details",
        "donors.load_failed": "Could not load donor",
        "donors.permission_body": "Only admin can delete donors.",
        "donors.confirm_body": (
            "Delete this donor and ALL their donations across every project?"
        ),
        "donors.import_failed": "Import failed",
        "donors.import_complete": "Import complete",
        "donors.imported_count": "Imported {count} donor(s).",
        "donors.import_link_title": "Import donors linked to this project",
        "donors.import_link_body": (
            "Open a project first, then import donors linked to it."
        ),
        "donors.import_link_result": (
            "New donors: {created}\n"
            "Existing donors reused: {reused}\n"
            "Linked donations: {donations}\n\n"
            "Columns: name, email, phone, pledged, paid, method, date, reference"
        ),
        "donors.export_title": "Export",
        "donors.export_empty": "No donors to export.",
        "donors.export_complete": "Export complete",
        "donors.export_saved": "Saved:\n{path}",
        "donors.export_failed": "Export failed",
        "donations.title": "Donations",
        "donations.record": "+ Record donation",
        "donations.note": (
            "Any registered donor can donate to this project. "
            "Record who collected each gift, then search by collector. "
            "Flow: pledged → collected by → payment → status."
        ),
        "donations.search_ph": (
            "Search donor, collector, status, method, reference, notes…"
        ),
        "donations.collected_by": "Collected by",
        "donations.all_collectors": "All collectors",
        "donations.sort_by": "Sort by",
        "donations.sort.date_desc": "Date · newest",
        "donations.sort.date_asc": "Date · oldest",
        "donations.sort.donor_asc": "Donor A–Z",
        "donations.sort.donor_desc": "Donor Z–A",
        "donations.sort.collector_asc": "Collector A–Z",
        "donations.sort.pledged_desc": "Pledged · high–low",
        "donations.sort.pledged_asc": "Pledged · low–high",
        "donations.sort.paid_desc": "Paid · high–low",
        "donations.sort.paid_asc": "Paid · low–high",
        "donations.sort.remaining_desc": "Remaining · high–low",
        "donations.sort.status": "Status",
        "donations.sort.method": "Method",
        "donations.record_payment": "Record payment",
        "donations.payment_history": "Payment history",
        "donations.by_collector": "By collector…",
        "donations.pay_tip": "Apply a payment toward the outstanding pledged balance.",
        "donations.history_tip": "See each installment: date, method, received by…",
        "donations.collector_tip": (
            "Search a staff user and see every donation they collected."
        ),
        "donations.count": "{count} donation(s)",
        "donations.showing": "Showing {shown} of {total} donation(s)",
        "donations.select_title": "Select donation",
        "donations.select_body": "Select a donation first.",
        "donations.setup_title": "Setup required",
        "donations.setup_body": "Add at least one donor first (Donors → Add donor).",
        "donations.nothing_title": "Nothing outstanding",
        "donations.nothing_body": "This donation is already fully paid.",
        "donations.confirm_body": "Delete this donation?",
        "expenses.title": "Expenses",
        "expenses.add": "+ Add expense",
        "expenses.search_ph": "Search title, category, notes, amount…",
        "expenses.sort_by": "Sort by",
        "expenses.sort.date_desc": "Date · newest",
        "expenses.sort.date_asc": "Date · oldest",
        "expenses.sort.title_asc": "Title A–Z",
        "expenses.sort.title_desc": "Title Z–A",
        "expenses.sort.category_asc": "Category A–Z",
        "expenses.sort.amount_desc": "Amount · high–low",
        "expenses.sort.amount_asc": "Amount · low–high",
        "expenses.summary": "{count} expense(s) · Total {total}",
        "expenses.summary_filtered": (
            "Showing {shown} of {total} · Filtered total {filtered} · Full total {full}"
        ),
        "expenses.select_title": "Select expense",
        "expenses.select_body": "Select an expense first.",
        "expenses.confirm_body": "Delete this expense?",
        "reports.title": "Reports & statistics",
        "reports.view": "View",
        "reports.overall": "Overall (all projects)",
        "reports.this_project": "This project only",
        "reports.refresh": "Refresh charts",
        "reports.print": "Print…",
        "reports.save_pdf": "Save PDF",
        "reports.subtitle": "Graphical fundraising insights.",
        "reports.subtitle_overall": (
            "Overall portfolio · {projects} project(s) · {donors} donor(s) · "
            "Net {net} · Charts colour-code the top projects by funds raised"
        ),
        "reports.subtitle_project": (
            "{name} · Target {target} · {fund_status} · Net {net} · "
            "Donors {donors} · Donations {donations}"
        ),
        "reports.need_project": "Select a project, or switch View to Overall (admin).",
        "reports.card_target_all": "All project goals",
        "reports.card_raised_all": "Paid across projects",
        "reports.card_pledged_all": "Committed total",
        "reports.card_expenses_all": "All project spend",
        "projects.title": "Projects",
        "projects.import": "Import file",
        "projects.import_linked": "Import projects + donors",
        "projects.add": "+ New project",
        "projects.note": (
            "Import projects alone, or import a sheet that creates projects and "
            "links donors in one go. Finished campaigns should be set to "
            "Archived (Completed is archived automatically)."
        ),
        "projects.search_ph": "Search by name or description…",
        "projects.status_filter": "Status",
        "projects.current": "Current (hide archived)",
        "projects.all_statuses": "All statuses",
        "projects.open_dashboard": "Open dashboard",
        "projects.count": "{count} project(s)",
        "projects.select_title": "Select project",
        "projects.select_body": "Select a project first.",
        "projects.permission_edit": "Only admin can edit projects.",
        "projects.permission_delete": "Only admin can delete projects.",
        "projects.confirm_body": (
            "Delete this project and its donations and expenses?\n"
            "Donors themselves are kept (they may give to other projects)."
        ),
        "users.title": "Users & access",
        "users.add": "+ Add user",
        "users.note": (
            "Admins access all projects. Project users may only work on projects you assign."
        ),
        "users.select_title": "Select user",
        "users.select_body": "Select a user first.",
        "users.not_allowed": "Not allowed",
        "users.not_allowed_body": "You cannot delete your own account while signed in.",
        "users.confirm_body": "Delete this user account?",
        "project_dashboard.title": "Project dashboard",
        "project_dashboard.select": "Select a project to view its dashboard.",
        "project_dashboard.not_found": "Project not found.",
        "project_dashboard.progress": "Fundraising progress",
        "project_dashboard.recent": "Recent donations",
        "project_dashboard.per_page": "Per page",
        "project_dashboard.status_line": (
            "Status: {status} · Fund status: {fund_status}"
        ),
        "project_dashboard.fund_line": (
            "{fund_status} · {pct}% of target · "
            "Remaining to target: {remaining} · "
            "Outstanding from donors: {outstanding} · "
            "Donors: {donors} · Donations: {donations}"
        ),
        "project_dashboard.page": "Page {page} of {max_page} · {total} donation(s)",
        "donor_item.no_contact": "No contact details",
        "donor_item.pledged": "Pledged {amount}  ·  ",
        "donor_item.paid": "Paid {amount}",
        "donor_item.left": "  ·  Left {amount}",
        "donor_item.counts": "{projects} project(s) · {donations} donation(s)",
        "donor_item.paid_tip": "View payment history — dates, methods, received by…",
        "main.working_on": "Working on: {name}",
        "main.select_project_title": "Select a project",
        "main.select_project_body": "Open a project from Overview or Projects first.",
        "main.access_denied": "Access denied",
        "main.access_denied_body": "You are not assigned to this project.",
        "main.not_found": "Not found",
        "main.not_found_body": "Project no longer exists.",
        "main.license": "License",
        "main.license_expired": "License expired",
        "main.license_expired_body": (
            "{message}\n\nThe app will close after you sign out."
        ),
        "backup.reminder_title": "Backup reminder",
        "backup.reminder_none": (
            "No database backup has been recorded on this PC yet.\n\n"
            "This version keeps data on one computer only. Export a backup "
            "from Settings, or enable backup-on-exit."
        ),
        "backup.reminder_days": (
            "The last backup on this PC was about {days} day(s) ago.\n\n"
            "Export a fresh copy from Settings → Data backup, or keep "
            "backup-on-exit enabled."
        ),
        "logout.title": "Log out",
        "logout.confirm": "Sign out of this session?",
        "dialog.validation": "Validation",
        "dialog.donation_title": "Donation details",
        "dialog.donation_payment_title": "Record payment",
        "dialog.donation.donor": "Donor *",
        "dialog.donation.donor_ph": "Search donor by name…",
        "dialog.donation.pledged": "Raised / pledged *",
        "dialog.donation.paid": "Paid amount",
        "dialog.donation.already_paid": "Already paid",
        "dialog.donation.this_payment": "This payment",
        "dialog.donation.pay_remaining": "Pay remaining",
        "dialog.donation.pay_remaining_tip": "Set this payment to the outstanding balance.",
        "dialog.donation.add_payment_tip": (
            "Amount received now — added on top of what is already paid."
        ),
        "dialog.donation.outstanding": "Still outstanding",
        "dialog.donation.status_after": "Status after save",
        "dialog.donation.method": "Payment method",
        "dialog.donation.collected_by": "Collected by *",
        "dialog.donation.collected_ph": "Search staff who collected…",
        "dialog.donation.date": "Date",
        "dialog.donation.reference": "Reference",
        "dialog.donation.reference_ph": "e.g. bank slip / cheque / M-Pesa ID",
        "dialog.donation.reference_help": (
            "Optional payment tracking ID — for example a bank transfer number, "
            "cheque number, mobile-money transaction ID, or receipt/voucher code. "
            "It does not affect totals or status; leave blank if unused."
        ),
        "dialog.donation.notes": "Notes",
        "dialog.donation.err_donor": "Select a donor from the list.",
        "dialog.donation.err_pledged": "Pledged amount must be positive.",
        "dialog.donation.err_paid": "Total paid cannot exceed pledged amount.",
        "dialog.donation.err_project": "No project selected.",
        "dialog.donation.err_collector": "Select who collected this donation.",
        "dialog.donor_title": "Donor details",
        "dialog.donor.name": "Name *",
        "dialog.donor.email": "Email",
        "dialog.donor.phone": "Phone",
        "dialog.donor.address": "Address",
        "dialog.donor.notes": "Notes",
        "dialog.donor.err_name": "Donor name is required.",
        "dialog.expense_title": "Expense details",
        "dialog.expense.title_field": "Title *",
        "dialog.expense.category": "Category",
        "dialog.expense.amount": "Amount *",
        "dialog.expense.date": "Date",
        "dialog.expense.notes": "Notes",
        "dialog.expense.err_title": "Title is required.",
        "dialog.expense.err_amount": "Amount must be positive.",
        "dialog.expense.err_project": "No project selected.",
        "dialog.project_title": "Project details",
        "dialog.project.name": "Project name *",
        "dialog.project.description": "Description",
        "dialog.project.target": "Target fund",
        "dialog.project.status": "Status",
        "dialog.project.status_tip": (
            "Set finished campaigns to Archived. They stay in history "
            "but are hidden from the default project list."
        ),
        "dialog.project.err_name": "Project name is required.",
        "dialog.project.err_target": "Target fund must be greater than zero.",
        "dialog.user_title": "User account",
        "dialog.user.username": "Username *",
        "dialog.user.full_name": "Full name",
        "dialog.user.password": "Password",
        "dialog.user.password_keep": "Leave blank to keep current",
        "dialog.user.password_required": "Required",
        "dialog.user.role": "Role",
        "dialog.user.active": "Active account",
        "dialog.user.assigned": "Assigned projects (for users):",
        "dialog.user.err_username": "Username is required.",
        "dialog.user.err_password": "Password is required for new users.",
        "dialog.user.err_projects": "Assign at least one project to a non-admin user.",
    },
    LANG_AR: {
        "app.name": "جمع التبرعات",
        "nav.overview": "نظرة عامة",
        "nav.projects": "المشاريع",
        "nav.dashboard": "لوحة المشروع",
        "nav.donors": "المتبرعون",
        "nav.donations": "التبرعات",
        "nav.expenses": "المصروفات",
        "nav.reports": "التقارير",
        "nav.users": "المستخدمون",
        "nav.settings": "الإعدادات",
        "nav.logout": "تسجيل الخروج",
        "nav.no_project": "لم يُحدَّد مشروع",
        "role.admin": "مسؤول",
        "role.user": "مستخدم",
        "common.save": "حفظ",
        "common.cancel": "إلغاء",
        "common.delete": "حذف",
        "common.edit": "تعديل",
        "common.add": "إضافة",
        "common.close": "إغلاق",
        "common.yes": "نعم",
        "common.no": "لا",
        "common.ready": "جاهز",
        "common.refresh": "تحديث",
        "common.search": "بحث",
        "common.import": "استيراد",
        "common.export": "تصدير",
        "common.open": "فتح",
        "common.previous": "‹ السابق",
        "common.next": "التالي ›",
        "common.select_first": "اختر عنصراً أولاً.",
        "common.no_project_title": "لا يوجد مشروع",
        "common.no_project_body": "افتح مشروعاً أولاً.",
        "common.confirm_delete": "تأكيد الحذف",
        "common.save_failed": "فشل الحفظ",
        "common.delete_failed": "فشل الحذف",
        "common.permission": "صلاحية",
        "common.all": "الكل",
        "col.id": "المعرّف",
        "col.date": "التاريخ",
        "col.donor": "المتبرع",
        "col.project": "المشروع",
        "col.status": "الحالة",
        "col.target": "الهدف",
        "col.pledged": "التعهّد",
        "col.raised": "المحصّل",
        "col.outstanding": "المتبقي",
        "col.paid": "المدفوع",
        "col.remaining": "الباقي",
        "col.method": "الطريقة",
        "col.reference": "المرجع",
        "col.fund_status": "حالة التمويل",
        "col.progress": "التقدّم",
        "col.name": "الاسم",
        "col.expenses": "المصروفات",
        "col.title": "العنوان",
        "col.category": "الفئة",
        "col.amount": "المبلغ",
        "col.notes": "ملاحظات",
        "col.collected_by": "جمّعها",
        "col.username": "اسم المستخدم",
        "col.full_name": "الاسم الكامل",
        "col.role": "الدور",
        "col.active": "نشط",
        "col.projects": "المشاريع",
        "card.projects": "المشاريع",
        "card.pledged": "التعهّدات",
        "card.raised": "المحصّل",
        "card.outstanding": "المتبقي",
        "card.expenses": "المصروفات",
        "card.target": "الهدف",
        "card.projects_hint": "متاحة لك",
        "card.pledged_hint": "ملتزم بها المتبرعون",
        "card.raised_hint": "مدفوع بالفعل",
        "card.outstanding_hint": "ما زال مستحقاً على المتبرعين",
        "card.outstanding_hint_detail": "التعهّد − المحصّل (ما زال مستحقاً)",
        "card.expenses_hint": "إنفاق مسجّل",
        "card.target_hint": "هدف جمع التبرعات",
        "card.raised_paid_hint": "المبلغ المدفوع",
        "card.pledged_committed_hint": "المبلغ المتعهّد به",
        "card.outstanding_owed_hint": "ما زال مستحقاً على المتبرعين",
        "card.expenses_project_hint": "إنفاق المشروع",
        "domain.active": "نشط",
        "domain.completed": "مكتمل",
        "domain.on_hold": "معلّق",
        "domain.archived": "مؤرشف",
        "domain.cash": "نقداً",
        "domain.bank_transfer": "تحويل بنكي",
        "domain.mobile_money": "محفظة جوال",
        "domain.cheque": "شيك",
        "domain.other": "أخرى",
        "domain.card": "بطاقة",
        "domain.online": "إلكتروني",
        "domain.admin": "مسؤول",
        "domain.user": "مستخدم",
        "domain.pending": "قيد الانتظار",
        "domain.remaining": "متبقي",
        "domain.not_started": "لم يبدأ",
        "domain.in_progress": "جارٍ",
        "domain.fully_funded": "مكتمل التمويل",
        "login.title": "تسجيل الدخول — جمع التبرعات",
        "login.eyebrow": "دخول آمن",
        "login.welcome": "مرحباً بعودتك",
        "login.subtitle": "سجّل الدخول لإدارة مشاريع جمع التبرعات الإسلامية والمتبرعين والتقارير.",
        "login.username": "اسم المستخدم",
        "login.password": "كلمة المرور",
        "login.username_ph": "أدخل اسم المستخدم",
        "login.password_ph": "أدخل كلمة المرور",
        "login.sign_in": "تسجيل الدخول",
        "login.forgot": "نسيت كلمة مرور المسؤول؟ تواصل مع الدعم",
        "login.hint": "أول تشغيل ينشئ حساب المسؤول — سيُطلب منك تغيير كلمة المرور.",
        "login.failed": "فشل تسجيل الدخول",
        "login.failed_body": "بيانات غير صحيحة أو الحساب غير نشط.",
        "login.license": "إدخال / تجديد رمز الترخيص",
        "login.empty": "أدخل اسم المستخدم وكلمة المرور.",
        "settings.title": "الإعدادات",
        "settings.note": (
            "خصّص مظهر هذا الجهاز. يظهر شعار منظمتك في الشريط الجانبي — "
            "أيقونة تطبيق MayleSoft تبقى كما هي."
        ),
        "settings.language": "اللغة",
        "settings.language_hint": (
            "الإنجليزية أو العربية أو الصومالية لواجهة التطبيق. "
            "العربية تستخدم تخطيطاً من اليمين إلى اليسار."
        ),
        "settings.language_restart": (
            "تم حفظ اللغة. سيُعاد تشغيل التطبيق لتحديث القوائم والشاشات بالكامل."
        ),
        "settings.theme": "لون السمة",
        "settings.theme_hint": "لون التمييز للأزرار والتمييز والتنقل.",
        "settings.mode": "وضع العرض",
        "settings.mode_hint": "النهار لمساحة فاتحة؛ الليل لمساحة داكنة.",
        "settings.mode.day": "نهار (فاتح)",
        "settings.mode.night": "ليل (داكن)",
        "settings.logo": "شعار المنظمة",
        "settings.logo_hint": (
            "يظهر في الشريط الجانبي تحت جلستك. هذا شعارك — "
            "وليس أيقونة تطبيق جمع التبرعات."
        ),
        "settings.logo_none": "لا يوجد شعار للمنظمة",
        "settings.logo_choose": "اختيار شعار…",
        "settings.logo_remove": "إزالة الشعار",
        "settings.backup": "نسخ احتياطي للبيانات",
        "settings.backup_hint": (
            "هذا التثبيت يخزّن البيانات على هذا الجهاز فقط — لا توجد قاعدة بيانات "
            "مشتركة بين عدة أجهزة في هذا الإصدار. صدّر نسخة بانتظام، أو استعد من ملف نسخ احتياطي."
        ),
        "settings.backup_on_exit": "كتابة نسخة احتياطية محلية عند إغلاق التطبيق",
        "settings.export_backup": "تصدير نسخة احتياطية…",
        "settings.restore_backup": "استعادة من نسخة احتياطية…",
        "settings.about": "حول",
        "settings.product": "المنتج",
        "settings.support_email": "بريد الدعم",
        "settings.install_id": "معرّف التثبيت",
        "overview.title": "نظرة عامة",
        "overview.subtitle": "محفظة جمع التبرعات لديك",
        "overview.projects": "المشاريع",
        "overview.open_dashboard": "فتح لوحة المشروع",
        "overview.role_admin": "مسؤول النظام",
        "overview.role_user": "مستخدم مشروع",
        "overview.signed_in": (
            "مسجّل الدخول باسم {name} · {role} · {donors} متبرع(ون) · "
            "المتبقي (ما زال مستحقاً): {outstanding} · "
            "صافي النقد (المحصّل − المصروفات): {net}"
        ),
        "donors.title": "المتبرعون",
        "donors.import": "استيراد متبرعين",
        "donors.import_link": "استيراد وربط بالمشروع",
        "donors.export_excel": "تصدير Excel",
        "donors.export_pdf": "تصدير PDF",
        "donors.add": "+ إضافة متبرع",
        "donors.note": (
            "استورد المتبرعين عالمياً، أو استخدم الاستيراد والربط لإضافتهم "
            "(مع تعهّد/دفع اختياري) إلى المشروع المفتوح. "
            "انقر البطاقة للاختيار · انقر مرتين للتفاصيل."
        ),
        "donors.search_ph": "ابحث بالاسم أو البريد أو الهاتف…",
        "donors.show": "عرض",
        "donors.all": "كل المتبرعين",
        "donors.this_project": "هذا المشروع فقط",
        "donors.per_page": "لكل صفحة",
        "donors.empty": "لا متبرعين بعد. أضف واحداً أو استورد من CSV/Excel.",
        "donors.page": "صفحة {page} من {max_page} · {total} متبرع(ون)",
        "donors.select_title": "اختر متبرعاً",
        "donors.select_body": "انقر بطاقة متبرع أولاً.",
        "donors.view_details": "عرض التفاصيل",
        "donors.load_failed": "تعذّر تحميل المتبرع",
        "donors.permission_body": "المسؤول فقط يمكنه حذف المتبرعين.",
        "donors.confirm_body": (
            "حذف هذا المتبرع وجميع تبرعاته في كل المشاريع؟"
        ),
        "donors.import_failed": "فشل الاستيراد",
        "donors.import_complete": "اكتمل الاستيراد",
        "donors.imported_count": "تم استيراد {count} متبرع(ين).",
        "donors.import_link_title": "استيراد متبرعين مرتبطين بهذا المشروع",
        "donors.import_link_body": (
            "افتح مشروعاً أولاً، ثم استورد المتبرعين المرتبطين به."
        ),
        "donors.import_link_result": (
            "متبرعون جدد: {created}\n"
            "متبرعون موجودون أُعيد استخدامهم: {reused}\n"
            "تبرعات مرتبطة: {donations}\n\n"
            "الأعمدة: name, email, phone, pledged, paid, method, date, reference"
        ),
        "donors.export_title": "تصدير",
        "donors.export_empty": "لا متبرعين للتصدير.",
        "donors.export_complete": "اكتمل التصدير",
        "donors.export_saved": "حُفظ في:\n{path}",
        "donors.export_failed": "فشل التصدير",
        "donations.title": "التبرعات",
        "donations.record": "+ تسجيل تبرع",
        "donations.note": (
            "أي متبرع مسجّل يمكنه التبرع لهذا المشروع. "
            "سجّل من جمع كل تبرع، ثم ابحث حسب الجامع. "
            "المسار: تعهّد ← جمعها ← دفع ← حالة."
        ),
        "donations.search_ph": (
            "ابحث عن متبرع، جامع، حالة، طريقة، مرجع، ملاحظات…"
        ),
        "donations.collected_by": "جمّعها",
        "donations.all_collectors": "كل الجامعين",
        "donations.sort_by": "ترتيب حسب",
        "donations.sort.date_desc": "التاريخ · الأحدث",
        "donations.sort.date_asc": "التاريخ · الأقدم",
        "donations.sort.donor_asc": "المتبرع أ–ي",
        "donations.sort.donor_desc": "المتبرع ي–أ",
        "donations.sort.collector_asc": "الجامع أ–ي",
        "donations.sort.pledged_desc": "التعهّد · الأعلى–الأدنى",
        "donations.sort.pledged_asc": "التعهّد · الأدنى–الأعلى",
        "donations.sort.paid_desc": "المدفوع · الأعلى–الأدنى",
        "donations.sort.paid_asc": "المدفوع · الأدنى–الأعلى",
        "donations.sort.remaining_desc": "الباقي · الأعلى–الأدنى",
        "donations.sort.status": "الحالة",
        "donations.sort.method": "الطريقة",
        "donations.record_payment": "تسجيل دفعة",
        "donations.payment_history": "سجل الدفعات",
        "donations.by_collector": "حسب الجامع…",
        "donations.pay_tip": "تطبيق دفعة على الرصيد المتعهّد المتبقي.",
        "donations.history_tip": "عرض كل قسط: التاريخ، الطريقة، المستلم…",
        "donations.collector_tip": (
            "ابحث عن موظف واعرض كل التبرعات التي جمعها."
        ),
        "donations.count": "{count} تبرع(ات)",
        "donations.showing": "عرض {shown} من {total} تبرع(ات)",
        "donations.select_title": "اختر تبرعاً",
        "donations.select_body": "اختر تبرعاً أولاً.",
        "donations.setup_title": "إعداد مطلوب",
        "donations.setup_body": "أضف متبرعاً واحداً على الأقل أولاً (المتبرعون ← إضافة متبرع).",
        "donations.nothing_title": "لا متبقي",
        "donations.nothing_body": "هذا التبرع مدفوع بالكامل.",
        "donations.confirm_body": "حذف هذا التبرع؟",
        "expenses.title": "المصروفات",
        "expenses.add": "+ إضافة مصروف",
        "expenses.search_ph": "ابحث بالعنوان أو الفئة أو الملاحظات أو المبلغ…",
        "expenses.sort_by": "ترتيب حسب",
        "expenses.sort.date_desc": "التاريخ · الأحدث",
        "expenses.sort.date_asc": "التاريخ · الأقدم",
        "expenses.sort.title_asc": "العنوان أ–ي",
        "expenses.sort.title_desc": "العنوان ي–أ",
        "expenses.sort.category_asc": "الفئة أ–ي",
        "expenses.sort.amount_desc": "المبلغ · الأعلى–الأدنى",
        "expenses.sort.amount_asc": "المبلغ · الأدنى–الأعلى",
        "expenses.summary": "{count} مصروف(ات) · الإجمالي {total}",
        "expenses.summary_filtered": (
            "عرض {shown} من {total} · إجمالي التصفية {filtered} · الإجمالي الكامل {full}"
        ),
        "expenses.select_title": "اختر مصروفاً",
        "expenses.select_body": "اختر مصروفاً أولاً.",
        "expenses.confirm_body": "حذف هذا المصروف؟",
        "reports.title": "التقارير والإحصاءات",
        "reports.view": "العرض",
        "reports.overall": "الإجمالي (كل المشاريع)",
        "reports.this_project": "هذا المشروع فقط",
        "reports.refresh": "تحديث الرسوم",
        "reports.print": "طباعة…",
        "reports.save_pdf": "حفظ PDF",
        "reports.subtitle": "رؤى رسومية لجمع التبرعات.",
        "reports.subtitle_overall": (
            "المحفظة الإجمالية · {projects} مشروع(ات) · {donors} متبرع(ون) · "
            "الصافي {net} · الرسوم تلوّن أبرز المشاريع حسب المبالغ المحصّلة"
        ),
        "reports.subtitle_project": (
            "{name} · الهدف {target} · {fund_status} · الصافي {net} · "
            "المتبرعون {donors} · التبرعات {donations}"
        ),
        "reports.need_project": "اختر مشروعاً، أو بدّل العرض إلى الإجمالي (للمسؤول).",
        "reports.card_target_all": "أهداف كل المشاريع",
        "reports.card_raised_all": "مدفوع عبر المشاريع",
        "reports.card_pledged_all": "إجمالي التعهّدات",
        "reports.card_expenses_all": "إنفاق كل المشاريع",
        "projects.title": "المشاريع",
        "projects.import": "استيراد ملف",
        "projects.import_linked": "استيراد مشاريع + متبرعين",
        "projects.add": "+ مشروع جديد",
        "projects.note": (
            "استورد المشاريع وحدها، أو ورقة تنشئ المشاريع وتربط المتبرعين دفعة واحدة. "
            "الحملات المنتهية تُضبط إلى مؤرشف "
            "(مكتمل يُؤرشف تلقائياً)."
        ),
        "projects.search_ph": "ابحث بالاسم أو الوصف…",
        "projects.status_filter": "الحالة",
        "projects.current": "الحالية (إخفاء المؤرشف)",
        "projects.all_statuses": "كل الحالات",
        "projects.open_dashboard": "فتح اللوحة",
        "projects.count": "{count} مشروع(ات)",
        "projects.select_title": "اختر مشروعاً",
        "projects.select_body": "اختر مشروعاً أولاً.",
        "projects.permission_edit": "المسؤول فقط يمكنه تعديل المشاريع.",
        "projects.permission_delete": "المسؤول فقط يمكنه حذف المشاريع.",
        "projects.confirm_body": (
            "حذف هذا المشروع وتبرعاته ومصروفاته؟\n"
            "المتبرعون أنفسهم يُحتفظ بهم (قد يتبرعون لمشاريع أخرى)."
        ),
        "users.title": "المستخدمون والصلاحيات",
        "users.add": "+ إضافة مستخدم",
        "users.note": (
            "المسؤولون يصلون لكل المشاريع. مستخدمو المشاريع يعملون فقط على ما تخصّصه لهم."
        ),
        "users.select_title": "اختر مستخدماً",
        "users.select_body": "اختر مستخدماً أولاً.",
        "users.not_allowed": "غير مسموح",
        "users.not_allowed_body": "لا يمكنك حذف حسابك وأنت مسجّل الدخول.",
        "users.confirm_body": "حذف حساب هذا المستخدم؟",
        "project_dashboard.title": "لوحة المشروع",
        "project_dashboard.select": "اختر مشروعاً لعرض لوحته.",
        "project_dashboard.not_found": "المشروع غير موجود.",
        "project_dashboard.progress": "تقدّم جمع التبرعات",
        "project_dashboard.recent": "أحدث التبرعات",
        "project_dashboard.per_page": "لكل صفحة",
        "project_dashboard.status_line": (
            "الحالة: {status} · حالة التمويل: {fund_status}"
        ),
        "project_dashboard.fund_line": (
            "{fund_status} · {pct}% من الهدف · "
            "المتبقي للهدف: {remaining} · "
            "المستحق من المتبرعين: {outstanding} · "
            "المتبرعون: {donors} · التبرعات: {donations}"
        ),
        "project_dashboard.page": "صفحة {page} من {max_page} · {total} تبرع(ات)",
        "donor_item.no_contact": "لا بيانات اتصال",
        "donor_item.pledged": "تعهّد {amount}  ·  ",
        "donor_item.paid": "مدفوع {amount}",
        "donor_item.left": "  ·  متبقي {amount}",
        "donor_item.counts": "{projects} مشروع(ات) · {donations} تبرع(ات)",
        "donor_item.paid_tip": "عرض سجل الدفعات — التواريخ والطرق والمستلم…",
        "main.working_on": "العمل على: {name}",
        "main.select_project_title": "اختر مشروعاً",
        "main.select_project_body": "افتح مشروعاً من النظرة العامة أو المشاريع أولاً.",
        "main.access_denied": "الوصول مرفوض",
        "main.access_denied_body": "لست مخصّصاً لهذا المشروع.",
        "main.not_found": "غير موجود",
        "main.not_found_body": "المشروع لم يعد موجوداً.",
        "main.license": "الترخيص",
        "main.license_expired": "انتهى الترخيص",
        "main.license_expired_body": (
            "{message}\n\nسيُغلق التطبيق بعد تسجيل الخروج."
        ),
        "backup.reminder_title": "تذكير بالنسخ الاحتياطي",
        "backup.reminder_none": (
            "لم يُسجَّل أي نسخ احتياطي لقاعدة البيانات على هذا الجهاز بعد.\n\n"
            "هذا الإصدار يحفظ البيانات على جهاز واحد فقط. صدّر نسخة من الإعدادات، "
            "أو فعّل النسخ عند الخروج."
        ),
        "backup.reminder_days": (
            "آخر نسخ احتياطي على هذا الجهاز كان منذ حوالي {days} يوماً.\n\n"
            "صدّر نسخة جديدة من الإعدادات ← النسخ الاحتياطي، أو أبقِ النسخ عند الخروج مفعّلاً."
        ),
        "logout.title": "تسجيل الخروج",
        "logout.confirm": "هل تريد إنهاء هذه الجلسة؟",
        "dialog.validation": "تحقق",
        "dialog.donation_title": "تفاصيل التبرع",
        "dialog.donation_payment_title": "تسجيل دفعة",
        "dialog.donation.donor": "المتبرع *",
        "dialog.donation.donor_ph": "ابحث عن متبرع بالاسم…",
        "dialog.donation.pledged": "التعهّد / المبلغ *",
        "dialog.donation.paid": "المبلغ المدفوع",
        "dialog.donation.already_paid": "مدفوع مسبقاً",
        "dialog.donation.this_payment": "هذه الدفعة",
        "dialog.donation.pay_remaining": "دفع المتبقي",
        "dialog.donation.pay_remaining_tip": "اضبط هذه الدفعة على الرصيد المستحق.",
        "dialog.donation.add_payment_tip": (
            "المبلغ المستلم الآن — يُضاف إلى ما دُفع مسبقاً."
        ),
        "dialog.donation.outstanding": "ما زال مستحقاً",
        "dialog.donation.status_after": "الحالة بعد الحفظ",
        "dialog.donation.method": "طريقة الدفع",
        "dialog.donation.collected_by": "جمّعها *",
        "dialog.donation.collected_ph": "ابحث عن الموظف الذي جمع…",
        "dialog.donation.date": "التاريخ",
        "dialog.donation.reference": "المرجع",
        "dialog.donation.reference_ph": "مثال: رقم تحويل / شيك / معرّف M-Pesa",
        "dialog.donation.reference_help": (
            "معرّف تتبّع اختياري للدفع — مثل رقم تحويل بنكي أو شيك أو "
            "معاملة محفظة جوال أو إيصال. لا يؤثر على الإجماليات أو الحالة؛ اتركه فارغاً إن لم يُستخدم."
        ),
        "dialog.donation.notes": "ملاحظات",
        "dialog.donation.err_donor": "اختر متبرعاً من القائمة.",
        "dialog.donation.err_pledged": "يجب أن يكون مبلغ التعهّد موجباً.",
        "dialog.donation.err_paid": "لا يمكن أن يتجاوز إجمالي المدفوع مبلغ التعهّد.",
        "dialog.donation.err_project": "لم يُحدَّد مشروع.",
        "dialog.donation.err_collector": "حدّد من جمع هذا التبرع.",
        "dialog.donor_title": "تفاصيل المتبرع",
        "dialog.donor.name": "الاسم *",
        "dialog.donor.email": "البريد",
        "dialog.donor.phone": "الهاتف",
        "dialog.donor.address": "العنوان",
        "dialog.donor.notes": "ملاحظات",
        "dialog.donor.err_name": "اسم المتبرع مطلوب.",
        "dialog.expense_title": "تفاصيل المصروف",
        "dialog.expense.title_field": "العنوان *",
        "dialog.expense.category": "الفئة",
        "dialog.expense.amount": "المبلغ *",
        "dialog.expense.date": "التاريخ",
        "dialog.expense.notes": "ملاحظات",
        "dialog.expense.err_title": "العنوان مطلوب.",
        "dialog.expense.err_amount": "يجب أن يكون المبلغ موجباً.",
        "dialog.expense.err_project": "لم يُحدَّد مشروع.",
        "dialog.project_title": "تفاصيل المشروع",
        "dialog.project.name": "اسم المشروع *",
        "dialog.project.description": "الوصف",
        "dialog.project.target": "هدف التمويل",
        "dialog.project.status": "الحالة",
        "dialog.project.status_tip": (
            "اضبط الحملات المنتهية على مؤرشف. تبقى في السجل "
            "لكن تُخفى من قائمة المشاريع الافتراضية."
        ),
        "dialog.project.err_name": "اسم المشروع مطلوب.",
        "dialog.project.err_target": "يجب أن يكون هدف التمويل أكبر من صفر.",
        "dialog.user_title": "حساب المستخدم",
        "dialog.user.username": "اسم المستخدم *",
        "dialog.user.full_name": "الاسم الكامل",
        "dialog.user.password": "كلمة المرور",
        "dialog.user.password_keep": "اتركه فارغاً للإبقاء على الحالية",
        "dialog.user.password_required": "مطلوب",
        "dialog.user.role": "الدور",
        "dialog.user.active": "حساب نشط",
        "dialog.user.assigned": "المشاريع المعيَّنة (للمستخدمين):",
        "dialog.user.err_username": "اسم المستخدم مطلوب.",
        "dialog.user.err_password": "كلمة المرور مطلوبة للمستخدمين الجدد.",
        "dialog.user.err_projects": "عيّن مشروعاً واحداً على الأقل لمستخدم غير مسؤول.",
    },
    LANG_SO: {
        "app.name": "Ururinta Lacagaha NGO",
        "nav.overview": "Dulmar",
        "nav.projects": "Mashaariic",
        "nav.dashboard": "Looxa mashruuca",
        "nav.donors": "Deeq-bixiyayaal",
        "nav.donations": "Deeqo",
        "nav.expenses": "Kharashaad",
        "nav.reports": "Warbixino",
        "nav.users": "Isticmaalayaal",
        "nav.settings": "Dejinta",
        "nav.logout": "Ka bax",
        "nav.no_project": "Mashruuc lama dooran",
        "role.admin": "ADMIN",
        "role.user": "USER",
        "common.save": "Kaydi",
        "common.cancel": "Jooji",
        "common.delete": "Tirtir",
        "common.edit": "Wax ka beddel",
        "common.add": "Kudar",
        "common.close": "Xir",
        "common.yes": "Haa",
        "common.no": "Maya",
        "common.ready": "Diyaar",
        "common.refresh": "Cusboonaysii",
        "common.search": "Raadi",
        "common.import": "Soo deji",
        "common.export": "Dhoofi",
        "common.open": "Fur",
        "common.previous": "‹ Hore",
        "common.next": "Xiga ›",
        "common.select_first": "Marka hore dooro shay.",
        "common.no_project_title": "Mashruuc ma jiro",
        "common.no_project_body": "Marka hore fur mashruuc.",
        "common.confirm_delete": "Xaqiiji tirtirka",
        "common.save_failed": "Kaydintu way fashilmay",
        "common.delete_failed": "Tirtirku wuu fashilmay",
        "common.permission": "Ogolaansho",
        "common.all": "Dhammaan",
        "col.id": "Aqoonsi",
        "col.date": "Taariikh",
        "col.donor": "Deeq-bixiye",
        "col.project": "Mashruuc",
        "col.status": "Xaalad",
        "col.target": "Hadaf",
        "col.pledged": "Ballanqaad",
        "col.raised": "La ururiyay",
        "col.outstanding": "Haray",
        "col.paid": "La bixiyay",
        "col.remaining": "Hadhay",
        "col.method": "Habka",
        "col.reference": "Tixraac",
        "col.fund_status": "Xaaladda lacagta",
        "col.progress": "Horumar",
        "col.name": "Magaca",
        "col.expenses": "Kharashaad",
        "col.title": "Cinwaan",
        "col.category": "Qayb",
        "col.amount": "Qaddar",
        "col.notes": "Qoraallo",
        "col.collected_by": "Ururiyay",
        "col.username": "Magaca isticmaale",
        "col.full_name": "Magaca buuxa",
        "col.role": "Doorka",
        "col.active": "Firfircoon",
        "col.projects": "Mashaariic",
        "card.projects": "MASHAARIIC",
        "card.pledged": "BALLANQAAD",
        "card.raised": "LA URURIYAY",
        "card.outstanding": "HARAY",
        "card.expenses": "KHARASHAAD",
        "card.target": "HADAF",
        "card.projects_hint": "Kuugu furan",
        "card.pledged_hint": "Deeq-bixiyayaashu way ballanqaadeen",
        "card.raised_hint": "Hore loo bixiyay",
        "card.outstanding_hint": "Weli deeq-bixiyayaasha ay ku leeyihiin",
        "card.outstanding_hint_detail": "Ballanqaad − la ururiyay (weli way ku leeyihiin)",
        "card.expenses_hint": "Kharash la diiwaangeliyay",
        "card.target_hint": "Hadafka ururinta",
        "card.raised_paid_hint": "Qaddarka la bixiyay",
        "card.pledged_committed_hint": "Qaddarka la ballanqaaday",
        "card.outstanding_owed_hint": "Weli deeq-bixiyayaasha ay ku leeyihiin",
        "card.expenses_project_hint": "Kharashka mashruuca",
        "domain.active": "Firfircoon",
        "domain.completed": "Dhammaystiran",
        "domain.on_hold": "La hakiyay",
        "domain.archived": "Kaydsan",
        "domain.cash": "Lacag caddaan",
        "domain.bank_transfer": "Rarid bangiga",
        "domain.mobile_money": "Lacag mobayl",
        "domain.cheque": "Jeeg",
        "domain.other": "Kale",
        "domain.card": "Kaadh",
        "domain.online": "Khadka",
        "domain.admin": "admin",
        "domain.user": "isticmaale",
        "domain.pending": "Sugaya",
        "domain.remaining": "Hadhay",
        "domain.not_started": "Weli ma bilowmin",
        "domain.in_progress": "Socda",
        "domain.fully_funded": "Si buuxda loo maalgeliyay",
        "login.title": "Galitaanka — Ururinta Lacagaha NGO",
        "login.eyebrow": "GELITAAN AMMAAN AH",
        "login.welcome": "Ku soo noqow",
        "login.subtitle": "Gal si aad u maamusho mashaariicda lacag-ururinta Islaamiga, deeq-bixiyayaasha iyo warbixinnada.",
        "login.username": "Magaca isticmaale",
        "login.password": "Erayga sirta ah",
        "login.username_ph": "Geli magaca isticmaale",
        "login.password_ph": "Geli erayga sirta ah",
        "login.sign_in": "Gal",
        "login.forgot": "Ma illowday erayga sirta admin? La xidhiidh taageerada",
        "login.hint": "Furitaanka ugu horreeya wuxuu abuuraa admin — waa lagu weydiin doonaa inaad beddesho erayga sirta.",
        "login.failed": "Gelitaanku wuu fashilmay",
        "login.failed_body": "Xog khaldan ama akoon aan firfircoonayn.",
        "login.license": "Geli / cusboonaysii koodhka shatiga",
        "login.empty": "Geli magaca isticmaale iyo erayga sirta ah.",
        "settings.title": "Dejinta",
        "settings.note": (
            "Shakhsiyeey muuqaalka kombiyuutarkan. Astaanta ururkaagu waxay ka muuqataa "
            "sidebar-ka — astaanta MayleSoft way is beddeli mayso."
        ),
        "settings.language": "Luqadda",
        "settings.language_hint": (
            "Ingiriisi, Carabi, ama Soomaali ee interface-ka app-ka. "
            "Carabigu wuxuu isticmaalaa jihada midig-ilaa-bidix."
        ),
        "settings.language_restart": (
            "Luqadda waa la keydiyay. App-ku wuu dib u bilaabi doonaa si menus-ka iyo shaashadaha ay u cusboonaadaan."
        ),
        "settings.theme": "Midabka mawduuca",
        "settings.theme_hint": "Midabka muhiimka ah ee badhamada, iftiinada, iyo navigation-ka.",
        "settings.mode": "Habka muujinta",
        "settings.mode_hint": "Maalintu waa iftiin; Habeenkuna waa mugdi.",
        "settings.mode.day": "Maalin (iftiin)",
        "settings.mode.night": "Habeen (mugdi)",
        "settings.logo": "Astaanta ururka",
        "settings.logo_hint": (
            "Waxaa lagu muujiyaa sidebar-ka hoostiisa. Tani waa astaantaada — "
            "ma aha icon-ka app-ka Ururinta Lacagaha."
        ),
        "settings.logo_none": "Astaan urur ma jirto",
        "settings.logo_choose": "Dooro astaan…",
        "settings.logo_remove": "Ka saar astaanta",
        "settings.backup": "Kaydadka xogta",
        "settings.backup_hint": (
            "Rakibiddani waxay xogta ku kaydisaa PC-gan oo keliya — ma jirto database "
            "la wadaago dhowr qalab. Si joogto ah u dhoofi kayd, ama ka soo celi fayl kayd ah."
        ),
        "settings.backup_on_exit": "Qor kayd maxalli ah marka app-ka la xidho",
        "settings.export_backup": "Dhoofi kayd…",
        "settings.restore_backup": "Ka soo celi kayd…",
        "settings.about": "Ku saabsan",
        "settings.product": "Alaabta",
        "settings.support_email": "Iimaylka taageerada",
        "settings.install_id": "Aqoonsiga rakibidda",
        "overview.title": "Dulmar",
        "overview.subtitle": "Mashruucyadaada ururinta lacagaha",
        "overview.projects": "Mashaariic",
        "overview.open_dashboard": "Fur looxa mashruuca",
        "overview.role_admin": "Maamulaha",
        "overview.role_user": "Isticmaale mashruuc",
        "overview.signed_in": (
            "Waxaad ku jirtaa sidii {name} · {role} · {donors} deeq-bixiye(yaal) · "
            "Haray (weli way ku leeyihiin): {outstanding} · "
            "Safiifka lacagta (la ururiyay − kharash): {net}"
        ),
        "donors.title": "Deeq-bixiyayaal",
        "donors.import": "Soo deji deeq-bixiyayaal",
        "donors.import_link": "Soo deji oo ku xidh mashruuca",
        "donors.export_excel": "Dhoofi Excel",
        "donors.export_pdf": "Dhoofi PDF",
        "donors.add": "+ Kudar deeq-bixiye",
        "donors.note": (
            "Soo deji deeq-bixiyayaal guud ahaan, ama soo deji oo ku xidh si aad ugu xidhid "
            "(ballanqaad/bixin ikhtiyaari ah) mashruuca furan. "
            "Guji kaarka si aad u doorato · labo jeer u dhagsii faahfaahinta."
        ),
        "donors.search_ph": "Raadi magac, iimayl, ama telefoon…",
        "donors.show": "Muuji",
        "donors.all": "Dhammaan deeq-bixiyayaasha",
        "donors.this_project": "Mashruucan oo keliya",
        "donors.per_page": "Boggiiba",
        "donors.empty": "Weli deeq-bixiye ma jiro. Mid ku dar ama ka soo deji CSV/Excel.",
        "donors.page": "Bogga {page} ee {max_page} · {total} deeq-bixiye(yaal)",
        "donors.select_title": "Dooro deeq-bixiye",
        "donors.select_body": "Marka hore guji kaarka deeq-bixiyaha.",
        "donors.view_details": "Eeg faahfaahinta",
        "donors.load_failed": "Lama soo rarayn deeq-bixiyaha",
        "donors.permission_body": "Admin oo keliya ayaa tirtiri kara deeq-bixiyayaasha.",
        "donors.confirm_body": (
            "Ma tirtiraysaa deeq-bixiyahan iyo DHAMMAAN deeqihiisa mashaariicda oo dhan?"
        ),
        "donors.import_failed": "Soo dejintu way fashilmay",
        "donors.import_complete": "Soo dejintu way dhammaatay",
        "donors.imported_count": "Waxaa la soo dejiyay {count} deeq-bixiye(yaal).",
        "donors.import_link_title": "Soo deji deeq-bixiyayaal ku xidhan mashruucan",
        "donors.import_link_body": (
            "Marka hore fur mashruuc, ka dibna soo deji deeq-bixiyayaasha ku xidhan."
        ),
        "donors.import_link_result": (
            "Deeq-bixiyayaal cusub: {created}\n"
            "Kuwa jira oo dib loo isticmaalay: {reused}\n"
            "Deeqo la xidhay: {donations}\n\n"
            "Tiirarka: name, email, phone, pledged, paid, method, date, reference"
        ),
        "donors.export_title": "Dhoofinta",
        "donors.export_empty": "Ma jiraan deeq-bixiyayaal la dhoofiyo.",
        "donors.export_complete": "Dhoofintu way dhammaatay",
        "donors.export_saved": "Waxaa lagu kaydiyay:\n{path}",
        "donors.export_failed": "Dhoofintu way fashilmay",
        "donations.title": "Deeqo",
        "donations.record": "+ Diiwaangeli deeq",
        "donations.note": (
            "Deeq-bixiye kasta oo diiwaangashan wuxuu deeqi karaa mashruucan. "
            "Diiwaangeli cidda ururisay, ka dibna raadi sida ururiyaha. "
            "Habka: ballanqaad → ururiyay → lacag-bixin → xaalad."
        ),
        "donations.search_ph": (
            "Raadi deeq-bixiye, ururiye, xaalad, hab, tixraac, qoraal…"
        ),
        "donations.collected_by": "Ururiyay",
        "donations.all_collectors": "Dhammaan ururiyayaasha",
        "donations.sort_by": "Kala saar",
        "donations.sort.date_desc": "Taariikh · ugu cusub",
        "donations.sort.date_asc": "Taariikh · ugu da’ weyn",
        "donations.sort.donor_asc": "Deeq-bixiye A–Z",
        "donations.sort.donor_desc": "Deeq-bixiye Z–A",
        "donations.sort.collector_asc": "Ururiye A–Z",
        "donations.sort.pledged_desc": "Ballanqaad · sare–hoose",
        "donations.sort.pledged_asc": "Ballanqaad · hoose–sare",
        "donations.sort.paid_desc": "La bixiyay · sare–hoose",
        "donations.sort.paid_asc": "La bixiyay · hoose–sare",
        "donations.sort.remaining_desc": "Hadhay · sare–hoose",
        "donations.sort.status": "Xaalad",
        "donations.sort.method": "Habka",
        "donations.record_payment": "Diiwaangeli lacag-bixin",
        "donations.payment_history": "Taariikhda lacag-bixinta",
        "donations.by_collector": "Sida ururiyaha…",
        "donations.pay_tip": "Ku dabaq lacag-bixin miisaanka ballanqaadka ee haray.",
        "donations.history_tip": "Eeg qayb kasta: taariikh, hab, cidda qaadatay…",
        "donations.collector_tip": (
            "Raadi shaqaale oo eeg deeq kasta oo uu ururiyay."
        ),
        "donations.count": "{count} deeq(o)",
        "donations.showing": "Waxaa la muujinayaa {shown} ka mid ah {total} deeq(o)",
        "donations.select_title": "Dooro deeq",
        "donations.select_body": "Marka hore dooro deeq.",
        "donations.setup_title": "Diyaarinta waa loo baahan yahay",
        "donations.setup_body": "Marka hore ku dar ugu yaraan hal deeq-bixiye (Deeq-bixiyayaal → Kudar).",
        "donations.nothing_title": "Waxba ma harin",
        "donations.nothing_body": "Deeqdan si buuxda ayaa loo bixiyay.",
        "donations.confirm_body": "Ma tirtiraysaa deeqdan?",
        "expenses.title": "Kharashaad",
        "expenses.add": "+ Kudar kharash",
        "expenses.search_ph": "Raadi cinwaan, qayb, qoraal, qaddar…",
        "expenses.sort_by": "Kala saar",
        "expenses.sort.date_desc": "Taariikh · ugu cusub",
        "expenses.sort.date_asc": "Taariikh · ugu da’ weyn",
        "expenses.sort.title_asc": "Cinwaan A–Z",
        "expenses.sort.title_desc": "Cinwaan Z–A",
        "expenses.sort.category_asc": "Qayb A–Z",
        "expenses.sort.amount_desc": "Qaddar · sare–hoose",
        "expenses.sort.amount_asc": "Qaddar · hoose–sare",
        "expenses.summary": "{count} kharash(aad) · Wadarta {total}",
        "expenses.summary_filtered": (
            "Waxaa la muujinayaa {shown} ka mid ah {total} · "
            "Wadarta shaandhaynta {filtered} · Wadarta buuxda {full}"
        ),
        "expenses.select_title": "Dooro kharash",
        "expenses.select_body": "Marka hore dooro kharash.",
        "expenses.confirm_body": "Ma tirtiraysaa kharashkan?",
        "reports.title": "Warbixino & tirakoob",
        "reports.view": "Aragga",
        "reports.overall": "Guud ahaan (dhammaan mashaariicda)",
        "reports.this_project": "Mashruucan oo keliya",
        "reports.refresh": "Cusboonaysii jaantusyada",
        "reports.print": "Daabac…",
        "reports.save_pdf": "Kaydi PDF",
        "reports.subtitle": "Aragtiyo jaantus leh oo ku saabsan ururinta lacagaha.",
        "reports.subtitle_overall": (
            "Guud ahaan · {projects} mashruuc(yo) · {donors} deeq-bixiye(yaal) · "
            "Safiif {net} · Jaantusyadu waxay midabeeyaan mashaariicda ugu sarreeya"
        ),
        "reports.subtitle_project": (
            "{name} · Hadaf {target} · {fund_status} · Safiif {net} · "
            "Deeq-bixiyayaal {donors} · Deeqo {donations}"
        ),
        "reports.need_project": "Dooro mashruuc, ama u beddel Aragga Guud (admin).",
        "reports.card_target_all": "Hadafyada dhammaan mashaariicda",
        "reports.card_raised_all": "La bixiyay mashaariicda oo dhan",
        "reports.card_pledged_all": "Wadarta ballanqaadka",
        "reports.card_expenses_all": "Kharashka dhammaan mashaariicda",
        "projects.title": "Mashaariic",
        "projects.import": "Soo deji fayl",
        "projects.import_linked": "Soo deji mashaariic + deeq-bixiyayaal",
        "projects.add": "+ Mashruuc cusub",
        "projects.note": (
            "Soo deji mashaariic keliya, ama xaashi abuura mashaariic oo xidha "
            "deeq-bixiyayaal hal jeer. Ololaha dhammaaday waa in loo dejiyaa "
            "Kaydsan (Dhammaystiran si toos ah ayaa loo kaydiyaa)."
        ),
        "projects.search_ph": "Raadi magac ama sharaxaad…",
        "projects.status_filter": "Xaalad",
        "projects.current": "Kan hadda (qari kaydsan)",
        "projects.all_statuses": "Dhammaan xaaladaha",
        "projects.open_dashboard": "Fur looxa",
        "projects.count": "{count} mashruuc(yo)",
        "projects.select_title": "Dooro mashruuc",
        "projects.select_body": "Marka hore dooro mashruuc.",
        "projects.permission_edit": "Admin oo keliya ayaa wax ka beddeli kara mashaariicda.",
        "projects.permission_delete": "Admin oo keliya ayaa tirtiri kara mashaariicda.",
        "projects.confirm_body": (
            "Ma tirtiraysaa mashruucan iyo deeqihiisa iyo kharashihiisa?\n"
            "Deeq-bixiyayaasha laftooda waa la hayaa (waxay deeqi karaan mashaariic kale)."
        ),
        "users.title": "Isticmaalayaal & gelitaanka",
        "users.add": "+ Kudar isticmaale",
        "users.note": (
            "Admintu waxay galaan dhammaan mashaariicda. Isticmaalayaasha mashruuca "
            "waxay ka shaqeeyaan oo keliya kuwa aad u qoondeyso."
        ),
        "users.select_title": "Dooro isticmaale",
        "users.select_body": "Marka hore dooro isticmaale.",
        "users.not_allowed": "Lama oggola",
        "users.not_allowed_body": "Ma tirtiri kartid akoonkaaga intaad ku jirto.",
        "users.confirm_body": "Ma tirtiraysaa akoonkan isticmaale?",
        "project_dashboard.title": "Looxa mashruuca",
        "project_dashboard.select": "Dooro mashruuc si aad u aragto looxiisa.",
        "project_dashboard.not_found": "Mashruuca lama helin.",
        "project_dashboard.progress": "Horumarka ururinta",
        "project_dashboard.recent": "Deeqihii dhawaan",
        "project_dashboard.per_page": "Boggiiba",
        "project_dashboard.status_line": (
            "Xaalad: {status} · Xaaladda lacagta: {fund_status}"
        ),
        "project_dashboard.fund_line": (
            "{fund_status} · {pct}% ee hadafka · "
            "Hadhay ee hadafka: {remaining} · "
            "Haray ee deeq-bixiyayaasha: {outstanding} · "
            "Deeq-bixiyayaal: {donors} · Deeqo: {donations}"
        ),
        "project_dashboard.page": "Bogga {page} ee {max_page} · {total} deeq(o)",
        "donor_item.no_contact": "Xog xiriir ma jirto",
        "donor_item.pledged": "Ballanqaad {amount}  ·  ",
        "donor_item.paid": "La bixiyay {amount}",
        "donor_item.left": "  ·  Hadhay {amount}",
        "donor_item.counts": "{projects} mashruuc(yo) · {donations} deeq(o)",
        "donor_item.paid_tip": "Eeg taariikhda lacag-bixinta — taariikho, habab, cidda qaadatay…",
        "main.working_on": "Waxaa laga shaqeynayaa: {name}",
        "main.select_project_title": "Dooro mashruuc",
        "main.select_project_body": "Marka hore ka fur mashruuc Dulmar ama Mashaariic.",
        "main.access_denied": "Gelitaanka waa la diiday",
        "main.access_denied_body": "Lagumau qoondeynin mashruucan.",
        "main.not_found": "Lama helin",
        "main.not_found_body": "Mashruucu mar dambe ma jiro.",
        "main.license": "Shatiga",
        "main.license_expired": "Shatigu wuu dhacay",
        "main.license_expired_body": (
            "{message}\n\nApp-ku wuu xidhi doonaa ka dib markaad ka baxdo."
        ),
        "backup.reminder_title": "Xusuusin kaydka",
        "backup.reminder_none": (
            "Weli lama diiwaangelin kayd database ah PC-gan.\n\n"
            "Noocani wuxuu xogta ku hayaa hal kombiyuutar. Ka dhoofi kayd Dejinta, "
            "ama daar kaydka marka la baxayo."
        ),
        "backup.reminder_days": (
            "Kaydka ugu dambeeyay PC-gan wuxuu ahaa qiyaastii {days} maalmood ka hor.\n\n"
            "Ka dhoofi nuqul cusub Dejinta → Kaydadka xogta, ama sii hay kaydka marka la baxayo."
        ),
        "logout.title": "Ka bax",
        "logout.confirm": "Ma ka baxaysaa fadhigan?",
        "dialog.validation": "Xaqiijin",
        "dialog.donation_title": "Faahfaahinta deeqda",
        "dialog.donation_payment_title": "Diiwaangeli lacag-bixin",
        "dialog.donation.donor": "Deeq-bixiye *",
        "dialog.donation.donor_ph": "Raadi deeq-bixiye magac…",
        "dialog.donation.pledged": "Ballanqaad / la ururiyay *",
        "dialog.donation.paid": "Qaddarka la bixiyay",
        "dialog.donation.already_paid": "Hore loo bixiyay",
        "dialog.donation.this_payment": "Lacag-bixintan",
        "dialog.donation.pay_remaining": "Bixi hadhay",
        "dialog.donation.pay_remaining_tip": "U deji lacag-bixintan miisaanka haray.",
        "dialog.donation.add_payment_tip": (
            "Qaddarka hadda la helay — waxaa lagu darayaa wixii hore loo bixiyay."
        ),
        "dialog.donation.outstanding": "Weli haray",
        "dialog.donation.status_after": "Xaaladda kaydinta ka dib",
        "dialog.donation.method": "Habka lacag-bixinta",
        "dialog.donation.collected_by": "Ururiyay *",
        "dialog.donation.collected_ph": "Raadi shaqaalaha ururiyay…",
        "dialog.donation.date": "Taariikh",
        "dialog.donation.reference": "Tixraac",
        "dialog.donation.reference_ph": "tusaale: rarid bangiga / jeeg / M-Pesa ID",
        "dialog.donation.reference_help": (
            "Aqoonsi raadraac oo ikhtiyaari ah — tusaale ahaan nambarka raridda bangiga, "
            "jeeg, macaamil lacag-mobayl, ama rasiid. Ma saameeyo wadarta ama xaaladda; "
            "ka tag haddii aan la isticmaalin."
        ),
        "dialog.donation.notes": "Qoraallo",
        "dialog.donation.err_donor": "Liiska ka dooro deeq-bixiye.",
        "dialog.donation.err_pledged": "Qaddarka ballanqaadku waa inuu noqdaa mid wanaagsan.",
        "dialog.donation.err_paid": "Wadarta la bixiyay kama badnaan karto ballanqaadka.",
        "dialog.donation.err_project": "Mashruuc lama dooran.",
        "dialog.donation.err_collector": "Dooro cidda ururisay deeqdan.",
        "dialog.donor_title": "Faahfaahinta deeq-bixiyaha",
        "dialog.donor.name": "Magaca *",
        "dialog.donor.email": "Iimayl",
        "dialog.donor.phone": "Telefoon",
        "dialog.donor.address": "Cinwaan",
        "dialog.donor.notes": "Qoraallo",
        "dialog.donor.err_name": "Magaca deeq-bixiyaha waa loo baahan yahay.",
        "dialog.expense_title": "Faahfaahinta kharashka",
        "dialog.expense.title_field": "Cinwaan *",
        "dialog.expense.category": "Qayb",
        "dialog.expense.amount": "Qaddar *",
        "dialog.expense.date": "Taariikh",
        "dialog.expense.notes": "Qoraallo",
        "dialog.expense.err_title": "Cinwaanku waa loo baahan yahay.",
        "dialog.expense.err_amount": "Qaddarku waa inuu noqdaa mid wanaagsan.",
        "dialog.expense.err_project": "Mashruuc lama dooran.",
        "dialog.project_title": "Faahfaahinta mashruuca",
        "dialog.project.name": "Magaca mashruuca *",
        "dialog.project.description": "Sharaxaad",
        "dialog.project.target": "Hadafka lacagta",
        "dialog.project.status": "Xaalad",
        "dialog.project.status_tip": (
            "Ololaha dhammaaday u deji Kaydsan. Way ku hadhaan taariikhda "
            "laakiin waa laga qariyaa liiska mashruuca ee caadiga ah."
        ),
        "dialog.project.err_name": "Magaca mashruuca waa loo baahan yahay.",
        "dialog.project.err_target": "Hadafka lacagtu waa inuu ka weynaadaa eber.",
        "dialog.user_title": "Akoonka isticmaale",
        "dialog.user.username": "Magaca isticmaale *",
        "dialog.user.full_name": "Magaca buuxa",
        "dialog.user.password": "Erayga sirta ah",
        "dialog.user.password_keep": "Ka tag si aad u ilaaliso kan hadda",
        "dialog.user.password_required": "Loo baahan yahay",
        "dialog.user.role": "Doorka",
        "dialog.user.active": "Akoon firfircoon",
        "dialog.user.assigned": "Mashaariicda loo qoondeeyay (isticmaalayaasha):",
        "dialog.user.err_username": "Magaca isticmaale waa loo baahan yahay.",
        "dialog.user.err_password": "Erayga sirta ayaa loo baahan yahay isticmaalayaasha cusub.",
        "dialog.user.err_projects": "U qoondee ugu yaraan hal mashruuc isticmaale aan admin ahayn.",
    },
}


def normalize_language(code: str | None) -> str:
    code = (code or LANG_EN).strip().lower()
    return code if code in _STRINGS else LANG_EN


def get_language() -> str:
    return _current


def is_rtl(code: str | None = None) -> bool:
    return normalize_language(code or _current) == LANG_AR


def set_language(code: str) -> str:
    global _current
    _current = normalize_language(code)
    return _current


def tr(key: str, **kwargs) -> str:
    table = _STRINGS.get(_current) or _STRINGS[LANG_EN]
    text = table.get(key) or _STRINGS[LANG_EN].get(key) or key
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, ValueError):
            pass
    return text


def td(value: object | None) -> str:
    """Translate a known English domain value; return as-is if unknown."""
    if value is None:
        return ""
    raw = str(value).strip()
    if not raw:
        return ""
    key = _DOMAIN_KEYS.get(raw.lower())
    if key:
        return tr(key)
    return raw


def apply_language_to_app(app: QApplication | None = None, code: str | None = None) -> str:
    """Set catalog + Qt layout direction (RTL for Arabic)."""
    lang = set_language(code if code is not None else _current)
    qapp = app or QApplication.instance()
    if qapp is not None:
        qapp.setLayoutDirection(
            Qt.LayoutDirection.RightToLeft
            if is_rtl(lang)
            else Qt.LayoutDirection.LeftToRight
        )
        qapp.setApplicationDisplayName(tr("app.name"))
    return lang


def restart_application() -> None:
    """Relaunch this process so translated widgets rebuild cleanly."""
    import sys

    from PySide6.QtCore import QProcess

    qapp = QApplication.instance()
    if getattr(sys, "frozen", False):
        QProcess.startDetached(sys.executable, list(sys.argv[1:]))
    else:
        QProcess.startDetached(sys.executable, list(sys.argv))
    if qapp is not None:
        qapp.quit()
