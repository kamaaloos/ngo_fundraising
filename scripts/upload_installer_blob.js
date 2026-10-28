/**
 * Upload the Windows installer to the MayleSoft Vercel Blob store (public).
 *
 * Prerequisites:
 * 1. Create a public Blob store in the Vercel project (Storage → Blob).
 * 2. Copy BLOB_READ_WRITE_TOKEN from the store into the environment
 *    (or .env.local — never commit the token).
 * 3. Place the built installer at:
 *      web/downloads/MayleSoft-Installer-1.1.0.exe
 *
 * Usage:
 *   set BLOB_READ_WRITE_TOKEN=vercel_blob_rw_...
 *   npm run upload:installer
 *
 * Writes web/download-config.json with the public CDN URL for the landing page.
 */

const fs = require("fs");
const path = require("path");

function loadEnvFile(filePath) {
  if (!fs.existsSync(filePath)) return;
  const text = fs.readFileSync(filePath, "utf8");
  for (const rawLine of text.split(/\r?\n/)) {
    const line = rawLine.trim();
    if (!line || line.startsWith("#")) continue;
    const eq = line.indexOf("=");
    if (eq < 1) continue;
    const key = line.slice(0, eq).trim();
    let value = line.slice(eq + 1).trim();
    if (
      (value.startsWith('"') && value.endsWith('"')) ||
      (value.startsWith("'") && value.endsWith("'"))
    ) {
      value = value.slice(1, -1);
    }
    if (!(key in process.env) || process.env[key] === "") {
      process.env[key] = value;
    }
  }
}

async function main() {
  const root = path.join(__dirname, "..");
  loadEnvFile(path.join(root, ".env"));
  loadEnvFile(path.join(root, ".env.local"));

  const token = (process.env.BLOB_READ_WRITE_TOKEN || "").trim();
  if (!token) {
    console.error(
      "Missing BLOB_READ_WRITE_TOKEN.\n" +
        "Add it to .env.local (see .env.example), then re-run:\n" +
        "  npm run upload:installer"
    );
    process.exit(1);
  }

  const version = process.env.INSTALLER_VERSION || "1.1.0";
  const fileName = `MayleSoft-Installer-${version}.exe`;
  const localPath = path.join(
    __dirname,
    "..",
    "web",
    "downloads",
    fileName
  );

  if (!fs.existsSync(localPath)) {
    console.error(`Installer not found:\n  ${localPath}`);
    console.error("Build it first (installer\\build_installer.bat), then copy to web\\downloads\\");
    process.exit(1);
  }

  const { put } = await import("@vercel/blob");
  const bytes = fs.readFileSync(localPath);
  console.log(`Uploading ${fileName} (${(bytes.length / (1024 * 1024)).toFixed(1)} MB)…`);

  const blob = await put(`downloads/${fileName}`, bytes, {
    access: "public",
    token,
    addRandomSuffix: false,
    allowOverwrite: true,
    multipart: true,
    contentType: "application/octet-stream",
    cacheControlMaxAge: 60 * 60 * 24 * 7,
  });

  const downloadUrl = blob.url.includes("?")
    ? `${blob.url}&download=1`
    : `${blob.url}?download=1`;

  const config = {
    version,
    fileName,
    url: blob.url,
    downloadUrl,
    uploadedAt: new Date().toISOString(),
    store: "MayleSoft Vercel Blob",
  };

  const configPath = path.join(__dirname, "..", "web", "download-config.json");
  fs.writeFileSync(configPath, JSON.stringify(config, null, 2) + "\n", "utf8");

  console.log("Uploaded.");
  console.log(`  Public URL:   ${blob.url}`);
  console.log(`  Download URL: ${downloadUrl}`);
  console.log(`  Config:       web/download-config.json`);
  console.log("Commit web/download-config.json and redeploy the landing page.");
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
