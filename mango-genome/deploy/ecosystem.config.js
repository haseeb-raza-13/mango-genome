/**
 * PM2 ecosystem config for Mango Genome Database
 *
 * Deployment:
 *   pm2 start deploy/ecosystem.config.js
 *   pm2 save
 *   pm2 startup   ← run the generated command to persist across reboots
 *
 * Logs:
 *   pm2 logs mango-backend --lines 100
 *   pm2 logs mango-frontend --lines 100
 */

// Adjust BASE_PATH to match where you uploaded the project on Hostinger
const BASE_PATH = process.env.DEPLOY_PATH || "/home/u123456789/domains/yourdomain.com/mango-genome";

module.exports = {
  apps: [
    // ── FastAPI backend ──────────────────────────────────────────────────────
    {
      name: "mango-backend",
      // uvicorn is invoked as a Python module so the venv interpreter is used
      script: `${BASE_PATH}/backend/venv/bin/python`,
      args: "-m uvicorn main:app --host 127.0.0.1 --port 8000 --workers 2",
      cwd: `${BASE_PATH}/backend`,
      env: {
        DB_PATH: `${BASE_PATH}/backend/db`,
        DATA_PATH: `${BASE_PATH}/backend/data`,
        LOG_DIR: `${BASE_PATH}/backend/logs`,
        BLAST_BIN: "",            // set to ~/tools/ncbi-blast-.../bin if not in system PATH
        CLUSTALO_BIN: "clustalo", // set to full path if not in system PATH
        CORS_ORIGINS: `["https://yourdomain.com","http://localhost:3000"]`,
      },
      autorestart: true,
      watch: false,
      max_memory_restart: "500M",
      log_date_format: "YYYY-MM-DD HH:mm:ss",
    },

    // ── Next.js frontend ─────────────────────────────────────────────────────
    {
      name: "mango-frontend",
      script: "npm",
      args: "start",
      cwd: `${BASE_PATH}/frontend`,
      env: {
        NODE_ENV: "production",
        PORT: 3000,
        FASTAPI_URL: "http://127.0.0.1:8000",
      },
      autorestart: true,
      watch: false,
      max_memory_restart: "400M",
      log_date_format: "YYYY-MM-DD HH:mm:ss",
    },
  ],
};
