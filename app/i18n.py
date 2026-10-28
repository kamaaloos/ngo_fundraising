"""App UI language (English, Arabic, Somali).

Use ``tr("key")`` for user-visible strings. Language is stored in UI settings
and applied at startup (layout direction + string catalog).
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
        "donors.title": "Donors",
        "donations.title": "Donations",
        "expenses.title": "Expenses",
        "reports.title": "Reports & statistics",
        "projects.title": "Projects",
        "users.title": "Users & access",
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
        "donors.title": "المتبرعون",
        "donations.title": "التبرعات",
        "expenses.title": "المصروفات",
        "reports.title": "التقارير والإحصاءات",
        "projects.title": "المشاريع",
        "users.title": "المستخدمون والصلاحيات",
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
        "donors.title": "Deeq-bixiyayaal",
        "donations.title": "Deeqo",
        "expenses.title": "Kharashaad",
        "reports.title": "Warbixino & tirakoob",
        "projects.title": "Mashaariic",
        "users.title": "Isticmaalayaal & gelitaanka",
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
