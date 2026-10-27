# NGO Fundraising Management System

Desktop fundraising app built with Python, PySide6, SQLite, and SQLAlchemy.

## What it does

- **Projects** with target funds, fundraising status, search/status filters, and project dashboards
- **Donors** (global for admins; project-scoped for assigned users) with search and pagination
- **Donations** flow: pledged amount → payment method → status
  (`Pending` / `Remaining` / `Completed` from paid vs pledged), with search/sort
- **Expenses** tracked per project, with search/sort
- **Reports** with graphical charts (payment methods, status, monthly raised, expense categories)
- **Auth**
  - Admin: all projects + user management + project assignment
  - User: only assigned projects
  - Default admin must change password on first sign-in

## Style

Centralized Qt stylesheet in `app/styles.py` (desktop equivalent of Bootstrap).
Cards use hover-raise shadow effects.

## Requirements

- Python 3.10+
- Windows, macOS, or Linux

## Install (Windows — developers)

```bat
py -3.10 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run (developers)

```bat
python main.py
```

**Demo data is OFF by default.** Customer and normal runs start with an empty database
(admin account only). To load sample projects/donors for QA:

```bat
set NGO_SEED_DEMO=1
python main.py
```

Or:

```bat
python scripts/seed_demo.py
```

### Customer Windows build

**1. Build the desktop app payload**

```bat
packaging\build_windows.bat
```

Creates `dist\NGOFundraising\` (and optionally the older Inno Setup exe if Inno is installed).

**2. Build the MayleSoft futuristic installer (recommended)**

```bat
cd installer
npm install
npm run dist
```

Ship: `installer\dist\MayleSoft-Installer-1.1.0.exe`  
See `installer\README.md` for UI preview (`npm start`) and payload replacement.

### Download landing page

Static site in `web/` (open `web/index.html` or host the `web` folder).

```bat
start web\index.html
```

The frozen build never auto-seeds demo data.

Default admin (first launch only):

- Username: `admin`
- Password: `admin123`
- You will be prompted to set a new password before the app opens.

### Forgot password (support-managed)

Each install gets an **Install ID** (shown on the Sign in screen).

On first admin setup the app issues a **recovery key once**. The customer must email
Install ID + recovery key to **kamaaloos@gmail.com**. The developer stores them in the
support registry (developer PC only).

**Customer forgot password / needs license extend**

1. Email **kamaaloos@gmail.com** and quote the **Install ID** from the Sign in screen
2. Support looks up the recovery key / issues a license code
3. For password: customer clicks **Forgot admin password? Contact support** and enters the key
4. For license: customer pastes the extension code in the license dialog
5. After password reset, sign in as `admin` / `admin123` and set a new password

**Developer registry**

```bat
python scripts/customer_registry.py add --name "Customer NGO" --install-id NGO-XXXXXXXXXX --recovery-key ABCD-EF01-2345-6789
python scripts/customer_registry.py find --install-id NGO-XXXXXXXXXX
python scripts/customer_registry.py list
```

Registry file (developer machine): `%LOCALAPPDATA%\MayleSoftSupport\customer_registry.json`

**Emergency offline reset** (support/developer only — not in customer builds):

```bat
python scripts/reset_admin_password.py --confirm-offline-reset
```

### App license / usage timer

New installs get a **30-day trial** automatically.

When time is running out or expired, the customer emails **kamaaloos@gmail.com** with their
**Install ID**. You issue an extension code:

```bat
python scripts/customer_registry.py extend --install-id NGO-XXXXXXXXXX --days 365
python scripts/customer_registry.py extend --install-id NGO-XXXXXXXXXX --until 2027-12-31
```

Customer pastes the code in the license dialog (startup, Sign in → **Enter / renew license code**, or status bar).

Expired licenses block Sign in until a valid code is applied.

## Database

Stored at:

```text
%LOCALAPPDATA%\NGOFundraisingManager\fundraising.sqlite3
```

Created automatically on first launch. Schema upgrades are **additive** (non-destructive).
Before each upgrade the app writes a timestamped backup next to the database file
(`fundraising_backup_YYYYMMDD_HHMMSS.sqlite3`).

Admins can also **Export backup…** / **Restore from backup…** under Settings → Data backup
(restore quits the app; reopen afterward).

## Tests

```bat
pytest
```

## Typical workflow

1. Sign in as admin and change the default password
2. Create a project (Projects → New project)
3. Create a user and assign projects (Users)
4. Open a project → add donors → record donations → log expenses → view reports

## Import / export

### Donors page

- **Import donors** — global donor list  
  `name,email,phone,address,notes`
- **Import & link to project** — create/find donors and attach them to the open project  
  `name,email,phone,pledged,paid,method,date,reference`
- **Export Excel** / **Export PDF**

### Projects page (admin)

- **Import file** — projects only  
  `name,description,target,status`
- **Import projects + donors** — create projects and link donors in one sheet  
  `project_name,target,status,donor_name,email,phone,pledged,paid,method,date`

Alternate headers like `goal`, `donor_name`, `mobile`, `full_name` are accepted.
