# Sample import files

CSV and Excel (`.xlsx`) samples for NGO Fundraising.

## For customers (installed app)

1. Open **Projects**, **Donors**, or **Expenses**
2. Click **Sample templates…**
3. Files are copied to:
   `Documents\NGO Fundraising\Import samples\`
4. Use **Import** and pick a file from that folder

(These templates are bundled inside the installer under `app/assets/samples`.)

## For developers

Repo copies live in `samples/import/` and `app/assets/samples/` (shipped with the build).

| File | Import from | Required columns |
|------|-------------|------------------|
| `sample_projects.*` | **Projects → Import file** | `name`, `target` (> 0); optional `description`, `status` |
| `sample_donors.*` | **Donors → Import donors** | `name`; optional `email`, `phone`, `address`, `notes` |
| `sample_donors_linked_to_project.*` | **Donors → Import & link** (project open) | `name`; optional pledge/payment columns |
| `sample_projects_with_donors.*` | **Projects → Import projects + donors** | `project_name`, `donor_name`; `target` for new projects |
| `sample_expenses.*` | **Expenses → Import expenses** (project open) | `title`, `amount`; optional `category`, `date`, `notes` |

Expense categories: `Operations`, `Materials`, `Travel`, `Marketing`, `Staff`, `Utilities`, `Other`.

Dates: prefer `YYYY-MM-DD`.
