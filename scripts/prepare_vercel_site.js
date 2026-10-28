/**
 * Copy web/ → public/ for Vercel static hosting.
 * Keeps the desktop PySide6 app out of the serverless/Python path.
 */
const fs = require("fs");
const path = require("path");

function copyDir(src, dest) {
  fs.mkdirSync(dest, { recursive: true });
  for (const entry of fs.readdirSync(src, { withFileTypes: true })) {
    const from = path.join(src, entry.name);
    const to = path.join(dest, entry.name);
    if (entry.isDirectory()) copyDir(from, to);
    else fs.copyFileSync(from, to);
  }
}

const root = path.join(__dirname, "..");
const out = path.join(root, "public");
fs.rmSync(out, { recursive: true, force: true });
copyDir(path.join(root, "web"), out);
console.log("Prepared public/ from web/ for Vercel.");
