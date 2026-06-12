# Deployment Guide — Hostinger Business Plan

## Prerequisites (run once via SSH)

### 1. Verify system tools
```bash
which blastn blastp clustalo
blastn -version
```

If BLAST+ is missing:
```bash
mkdir -p ~/tools && cd ~/tools
wget https://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/LATEST/ncbi-blast-2.16.0+-x64-linux.tar.gz
tar -xzf ncbi-blast-*.tar.gz
# Add to PATH or set BLAST_BIN in ecosystem.config.js
```

If Clustal Omega is missing:
```bash
wget http://www.clustal.org/omega/clustal-omega-1.2.4-Ubuntu-x86_64 -O ~/tools/clustalo
chmod +x ~/tools/clustalo
# Set CLUSTALO_BIN=~/tools/clustalo in ecosystem.config.js
```

### 2. Install PM2 log rotate (once)
```bash
pm2 install pm2-logrotate
pm2 set pm2-logrotate:max_size 50M
pm2 set pm2-logrotate:retain 7
```

---

## Deploy Steps

```bash
# 1. Upload project (from your machine)
rsync -av --exclude='node_modules' --exclude='.next' --exclude='venv' \
  mango-genome/ user@yourdomain.com:~/domains/yourdomain.com/mango-genome/

# 2. SSH into server
ssh user@yourdomain.com

# 3. Set up Python virtualenv
cd ~/domains/yourdomain.com/mango-genome/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Symlink or copy data directories (if not in the project folder)
# backend/db  → should contain BLAST index files (.nsq, .nsq, etc.)
# backend/data → should contain .fasta files

# 5. Build Next.js
cd ~/domains/yourdomain.com/mango-genome/frontend
npm install
npm run build

# 6. Edit ecosystem.config.js — update BASE_PATH and domain/CORS_ORIGINS
nano ~/domains/yourdomain.com/mango-genome/deploy/ecosystem.config.js

# 7. Start both services
cd ~/domains/yourdomain.com/mango-genome
pm2 start deploy/ecosystem.config.js
pm2 save
pm2 startup   # follow the printed command to persist across reboots
```

---

## Hostinger hPanel — Node.js App Settings

In hPanel → **Advanced → Node.js**:
- Application root: `domains/yourdomain.com/mango-genome/frontend`
- Application startup file: `server.js`  (Next.js creates this in `.next/`)
- Or leave as `npm start` equivalent configured via PM2

Hostinger's reverse proxy will forward port 80/443 → your Node.js port 3000 automatically.
FastAPI on port 8000 is **only accessible from localhost** — never exposed publicly.

---

## Monitoring

```bash
# Live status
pm2 status

# Real-time logs
pm2 logs mango-backend --lines 100
pm2 logs mango-frontend --lines 100

# Search error logs
grep "ERROR\|CRITICAL" ~/domains/.../mango-genome/backend/logs/backend.log

# BLAST-specific logs
tail -f ~/domains/.../mango-genome/backend/logs/blast.log
```

---

## Updating After Code Changes

```bash
# Upload new code
rsync -av --exclude='node_modules' --exclude='.next' --exclude='venv' \
  mango-genome/ user@yourdomain.com:~/domains/yourdomain.com/mango-genome/

# Rebuild frontend
cd ~/domains/yourdomain.com/mango-genome/frontend && npm run build

# Restart services
pm2 reload mango-frontend
pm2 reload mango-backend
```
