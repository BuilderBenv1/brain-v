/**
 * sync-data.js — Copy Brain-V data into the dashboard for static builds.
 *
 * Copies hypothesis files, beliefs, stats, scores, and failed approaches
 * into dashboard/data/ so the Next.js app can read them at build time
 * regardless of whether the parent directory exists (e.g. on Vercel).
 *
 * Run before `next build`:
 *   node scripts/sync-data.js
 */

const fs = require("fs");
const path = require("path");

const BRAIN_ROOT = path.resolve(__dirname, "../..");
const DATA_DIR = path.resolve(__dirname, "../data");

function ensureDir(dir) {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
}

function copyJsonFiles(srcDir, destDir) {
  if (!fs.existsSync(srcDir)) return 0;
  ensureDir(destDir);
  let count = 0;
  for (const file of fs.readdirSync(srcDir)) {
    if (file.endsWith(".json")) {
      fs.copyFileSync(path.join(srcDir, file), path.join(destDir, file));
      count++;
    }
  }
  return count;
}

function copyFile(src, dest) {
  if (!fs.existsSync(src)) return false;
  ensureDir(path.dirname(dest));
  fs.copyFileSync(src, dest);
  return true;
}

console.log("[sync-data] Syncing Brain-V data into dashboard/data/...");

ensureDir(DATA_DIR);

// Hypotheses
const hCount = copyJsonFiles(
  path.join(BRAIN_ROOT, "hypotheses"),
  path.join(DATA_DIR, "hypotheses")
);
console.log(`  hypotheses: ${hCount} files`);

// Beliefs
const beliefsOk = copyFile(
  path.join(BRAIN_ROOT, "scripts/beliefs.json"),
  path.join(DATA_DIR, "beliefs.json")
);
console.log(`  beliefs: ${beliefsOk ? "ok" : "missing"}`);

// Stats
const statsOk = copyFile(
  path.join(BRAIN_ROOT, "raw/perception/voynich-stats.json"),
  path.join(DATA_DIR, "voynich-stats.json")
);
console.log(`  stats: ${statsOk ? "ok" : "missing"}`);

// Scores
const sCount = copyJsonFiles(
  path.join(BRAIN_ROOT, "outputs/scores"),
  path.join(DATA_DIR, "scores")
);
console.log(`  scores: ${sCount} files`);

// Failed approaches
const failedOk = copyFile(
  path.join(BRAIN_ROOT, "raw/corpus/failed-approaches.json"),
  path.join(DATA_DIR, "failed-approaches.json")
);
console.log(`  failed-approaches: ${failedOk ? "ok" : "missing"}`);

console.log("[sync-data] Done.");
