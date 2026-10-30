# Move NGO Fundraising data between a PC and a laptop

This guide is for **admins**. NGO Fundraising keeps data on **one computer at a time**. There is no live sync between machines. You move a full backup file from one computer to the other.

## Important

- **Restore replaces all data** on the receiving computer with the backup.
- Do **not** work on both computers at the same time and expect them to merge.
- Decide which machine is the **active** one after each move.
- You need the **admin** account for Export / Restore.

---

## A → B: Copy data from PC to laptop (or laptop to PC)

### On the computer that has the up-to-date data (source)

1. Open **NGO Fundraising** and sign in as **admin**.
2. Go to **Settings**.
3. Under **Data backup**, click **Export backup…**.
4. Save the file somewhere easy to find (for example Desktop or Documents).  
   Example name: `NGO_Fundraising_backup_20261030_153000.sqlite3`
5. Copy that file to a USB stick, email, OneDrive, or shared folder.

### On the other computer (destination)

1. Install NGO Fundraising if it is not installed yet, then open it and sign in as **admin**.
2. Go to **Settings → Data backup**.
3. Click **Restore from backup…**.
4. Choose the backup file you copied from the first computer.
5. Confirm when asked. The app will close after a successful restore.
6. Open NGO Fundraising again. Your projects, donors, donations, and expenses should match the source computer.

---

## Recommended routine (home + office)

| Situation | What to do |
|-----------|------------|
| You finish work on the **PC** and will continue on the **laptop** | Export on the PC → copy file → Restore on the laptop. Then use only the laptop until you move back. |
| You finish on the **laptop** and return to the **PC** | Export on the laptop → Restore on the PC. Then use only the PC. |
| You only need a safety copy | Export backup regularly (or keep **Write a local backup when quitting** enabled). Keep the file off the computer (USB / cloud). |

---

## Tips

- Give backup files clear names and dates so you do not restore an old file by mistake.
- After restore, check **Overview** or a known project to confirm the data looks right.
- License and Install ID are per computer; moving data does not move your Windows license registration.
- If restore fails, keep the backup file and contact MayleSoft support with your **Install ID** (shown in Settings → About).

---

## What this version does *not* do

- No automatic sync between PC and laptop  
- No shared database over the network  
- No merging of two different working copies  

For this version, **export → transfer → restore** is the supported way to exchange data.
