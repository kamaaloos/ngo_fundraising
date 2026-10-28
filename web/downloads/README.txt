Customer installer (not committed — too large for git / Vercel static):

  MayleSoft-Installer-1.1.0.exe

Build:

  installer\build_installer.bat

Host on MayleSoft Vercel Blob (recommended for the landing page):

  1. Vercel → Project → Storage → create/open public Blob store (MayleSoft)
  2. Copy BLOB_READ_WRITE_TOKEN into .env.local (see .env.example)
  3. npm install
  4. npm run upload:installer
  5. Commit web/download-config.json (public URL only) and redeploy

Do not ship NGOFundraising-Setup-*.exe — that opens a separate Inno Setup window.
