import fs from "fs/promises";
import path from "path";
import crypto from "crypto";

export async function walkFiles(dir: string): Promise<string[]> {
  const out: string[] = [];
  async function walk(d: string) {
    const entries = await fs.readdir(d, { withFileTypes: true });
    for (const e of entries) {
      const full = path.join(d, e.name);
      if (e.isDirectory()) await walk(full);
      else if (e.isFile() && (full.endsWith(".md") || full.endsWith(".txt"))) out.push(full);
    }
  }
  await walk(dir);
  return out;
}

export async function readUtf8(filePath: string): Promise<string> {
  return fs.readFile(filePath, "utf8");
}

export function extractTitle(content: string, filePath: string): string {
  if (filePath.endsWith(".md")) {
    const firstH1 = content.split(/\r?\n/).find((l) => l.trim().startsWith("#"));
    if (firstH1) return firstH1.replace(/^#+\s*/, "").trim();
  }
  return path.basename(filePath, path.extname(filePath));
}

export function makeDocId(sourcePath: string): string {
  return crypto.createHash("sha256").update(sourcePath).digest("hex");
}