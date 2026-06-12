import fs from "fs";
import path from "path";

const LOG_DIR = path.join(process.cwd(), "logs");

function ensureLogDir() {
  if (!fs.existsSync(LOG_DIR)) {
    fs.mkdirSync(LOG_DIR, { recursive: true });
  }
}

function write(level: string, msg: string, extra?: string) {
  const line = `${new Date().toISOString()} [${level}] ${msg}${extra ? " " + extra : ""}\n`;
  // Also log to console so PM2 captures it
  if (level === "ERROR") {
    console.error(line.trim());
  } else {
    console.log(line.trim());
  }
  try {
    ensureLogDir();
    fs.appendFileSync(path.join(LOG_DIR, "frontend.log"), line, "utf8");
  } catch {
    // don't crash if log write fails
  }
}

export const logger = {
  info: (msg: string, meta?: object) => write("INFO", msg, meta ? JSON.stringify(meta) : undefined),
  warn: (msg: string, meta?: object) => write("WARN", msg, meta ? JSON.stringify(meta) : undefined),
  error: (msg: string, err?: unknown) =>
    write(
      "ERROR",
      msg,
      err instanceof Error ? err.stack : err !== undefined ? String(err) : undefined
    ),
};
