/**
 * Copy the PyInstaller NGOFundraising build into installer/payload.
 * Replace payload contents with your own app files for other products.
 */
const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..");
const repoRoot = path.resolve(root, "..");
const source = path.join(repoRoot, "dist", "NGOFundraising");
const dest = path.join(root, "payload");

function rimraf(dir) {
  if (!fs.existsSync(dir)) return;
  fs.rmSync(dir, { recursive: true, force: true });
}

function copyDir(src, dst) {
  fs.mkdirSync(dst, { recursive: true });
  for (const entry of fs.readdirSync(src, { withFileTypes: true })) {
    const from = path.join(src, entry.name);
    const to = path.join(dst, entry.name);
    if (entry.isDirectory()) copyDir(from, to);
    else fs.copyFileSync(from, to);
  }
}

if (!fs.existsSync(source)) {
  console.error(
    "Missing app payload:\n  " +
      source +
      "\n\nBuild it first:\n  packaging\\build_windows.bat\n" +
      "(or at least run PyInstaller so dist\\NGOFundraising exists)"
  );
  process.exit(1);
}

const exe = path.join(source, "NGOFundraising.exe");
if (!fs.existsSync(exe)) {
  console.error("NGOFundraising.exe not found in", source);
  process.exit(1);
}

console.log("Syncing payload…");
console.log("  from:", source);
console.log("  to:  ", dest);
rimraf(dest);
copyDir(source, dest);
console.log("Payload ready.");
