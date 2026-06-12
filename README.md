# Mango Genome Database

A full-stack bioinformatics web application for exploring, searching, and comparing mango (*Mangifera indica*) genome sequences across five cultivars. Provides BLAST sequence search, Multiple Sequence Alignment (MSA), and curated FASTA downloads — all through a browser-based interface built on Next.js and FastAPI.

**Live site:** [mangodb.cloud](https://mangodb.cloud)

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Genome Data](#genome-data)
- [Project Structure](#project-structure)
- [Local Development](#local-development)
- [Environment Variables](#environment-variables)
- [Database Setup (DVC)](#database-setup-dvc)
- [Deployment](#deployment)
- [API Reference](#api-reference)
- [License](#license)

---

## Overview

This project migrates the original Streamlit-based Mango Genome Database to a production-grade full-stack application. The original Streamlit app had non-functional BLAST and MSA tools in the hosted environment due to binary dependency and process management limitations. This rewrite resolves those issues by separating concerns into:

- A **Next.js frontend** served by Phusion Passenger on Hostinger, handling all UI and proxying API calls
- A **FastAPI backend** running as a child process of the Node.js server, executing BLAST+ and Clustal Omega as subprocesses and returning results as JSON with embedded base64 plots

---

## Features

### BLAST Search
- Nucleotide (blastn) and protein (blastp) search
- 5 nucleotide databases and 4 protein databases
- Tabular results with 12 standard BLAST columns (query coverage, identity, e-value, bit score, etc.)
- Three auto-generated plots: alignment length distribution, identity vs. e-value scatter, bit score distribution
- CSV export of results

### Multiple Sequence Alignment (MSA)
- Upload FASTA files or paste sequences directly
- Alignment via Clustal Omega 1.2.4
- Aligned FASTA output with copy-to-clipboard
- Four visualisation plots: pairwise identity heatmap, base frequency chart, dot plot, identity distribution
- Downloadable alignment report

### Downloads
- Full FASTA files for all cultivars (nucleotide and protein)
- Streamed directly from the backend — no intermediate cloud storage

### Static Pages
- About the Project, Our Work, Literature, Disclaimer
- User Guide, Contact Us

---

## Architecture

```
Browser
  │  HTTPS (port 443)
  ▼
Apache + Phusion Passenger          (Hostinger Business Plan)
  │  proxies to Node.js
  ▼
Next.js standalone server           ~/domains/mangodb.cloud/nodejs/server.js
  ├── App Router pages              /blast  /msa  /downloads  /about  /help
  ├── /pages/api/blast              ─┐
  ├── /pages/api/blast-databases    ─┤ server-side proxy routes
  ├── /pages/api/msa                ─┤ (never exposed to browser)
  └── /pages/api/downloads/[file]  ─┘
            │  HTTP  127.0.0.1:8000
            ▼
FastAPI (uvicorn)                   ~/domains/mangodb.cloud/backend/
  ├── GET  /health
  ├── GET  /blast/databases
  ├── POST /blast                   → blastn / blastp subprocess
  ├── POST /msa                     → clustalo subprocess
  └── GET  /files/{filename}        → streams FASTA from db/
```

The FastAPI process is spawned by `server.js` on startup — no separate process manager required. The browser communicates only with Next.js; port 8000 is never publicly exposed.

---

## Tech Stack

### Frontend
| Technology | Version | Purpose |
|---|---|---|
| Next.js | 16.2.9 | App Router, SSR, API proxy routes |
| TypeScript | 5.x | Type safety across components and hooks |
| Tailwind CSS | 3.4 | Dark scientific theme (`#0a0f1e` / `#00d4aa`) |
| TanStack Table | 8.19 | Sortable, filterable BLAST results table |
| react-dropzone | 14.2 | FASTA file upload with drag-and-drop |
| lucide-react | 0.400 | Icon set |

### Backend
| Technology | Version | Purpose |
|---|---|---|
| FastAPI | 0.136 | REST API with automatic OpenAPI docs |
| uvicorn | 0.49 | ASGI server |
| BioPython | 1.83+ | Sequence I/O (`SeqIO`), alignment stats |
| matplotlib | 3.8+ | Server-side plot generation (returned as base64 PNG) |
| pandas | 2.1+ | BLAST TSV result parsing |
| seaborn | 0.13+ | Heatmap and statistical plots |
| python-dotenv | — | Environment configuration |

### Bioinformatics Tools
| Tool | Version | Notes |
|---|---|---|
| NCBI BLAST+ | 2.16.0 | Installed at `~/tools/blast/bin/` |
| Clustal Omega | 1.2.4 | Installed via micromamba from bioconda; wrapper script sets `LD_LIBRARY_PATH` |

### Infrastructure
| Component | Details |
|---|---|
| Hosting | Hostinger Business Plan |
| Web server | Apache + Phusion Passenger (Node.js 22) |
| Python | 3.11 (CloudLinux selector) |
| OS | CloudLinux with CageFS |
| Code versioning | Git |
| Data versioning | DVC 3.67 with SSH remote on Hostinger |

---

## Genome Data

Five mango cultivars are included, each with nucleotide and/or protein sequences:

| Cultivar | Origin | Nucleotide | Protein |
|---|---|---|---|
| Chaunsa / Zill | China | ✓ | ✓ |
| Keitt | Israel | ✓ | ✓ |
| Kent | Mexico | ✓ | ✓ |
| Langra | Pakistan | ✓ | — |
| Mod / Local | Pakistan | — | ✓ |

BLAST databases are pre-built with `makeblastdb` and stored in `backend/db/` (268 MB, 38 files). This directory is tracked with DVC — see [Database Setup](#database-setup-dvc).

---

## Project Structure

```
mango-genome/
├── frontend/                          Next.js application
│   ├── src/
│   │   ├── app/                       App Router pages
│   │   │   ├── blast/page.tsx
│   │   │   ├── msa/page.tsx
│   │   │   ├── downloads/page.tsx
│   │   │   ├── about/                 About, Disclaimer, Work, Literature
│   │   │   └── help/                  User Guide, Contact
│   │   ├── pages/api/                 Server-side proxy routes
│   │   │   ├── blast.ts
│   │   │   ├── blast-databases.ts
│   │   │   ├── msa.ts
│   │   │   └── downloads/[filename].ts
│   │   ├── components/
│   │   │   ├── layout/               AppHeader, Sidebar, AppFooter
│   │   │   ├── blast/                BlastForm, BlastResultsTable, BlastCharts
│   │   │   └── msa/                  MsaForm, MsaAlignmentView, MsaCharts
│   │   ├── hooks/                    useBlast.ts, useMsa.ts
│   │   ├── lib/                      logger.ts, api.ts
│   │   └── types/                    blast.ts, msa.ts
│   └── public/images/                Logos and gallery images
│
├── backend/                           FastAPI application
│   ├── main.py                        App entry point, CORS, middleware, logging
│   ├── requirements.txt
│   ├── routers/
│   │   ├── blast.py                   GET /blast/databases, POST /blast
│   │   ├── msa.py                     POST /msa
│   │   └── files.py                   GET /files/{filename}
│   ├── services/
│   │   ├── blast_service.py           BLAST subprocess + result parsing + plots
│   │   └── msa_service.py             Clustal Omega subprocess + alignment + plots
│   ├── schemas/
│   │   ├── blast.py                   BlastRequest, BlastHit, BlastResponse
│   │   └── msa.py                     MsaRequest, MsaResponse, AlignmentStats
│   ├── utils/
│   │   ├── fasta_utils.py             gc_content(), validate_fasta()
│   │   └── plot_utils.py              fig_to_base64(fig)
│   ├── data/                          Stub FASTA files (git-tracked)
│   └── db/                            BLAST databases 268 MB (DVC-tracked)
│
└── deploy/
    └── ecosystem.config.js            PM2 / Passenger deployment config
```

---

## Local Development

### Prerequisites

- Node.js 18+
- Python 3.11+
- NCBI BLAST+ (`blastn`, `blastp` on PATH or configured via `BLAST_BIN`)
- Clustal Omega (`clustalo` on PATH or configured via `CLUSTALO_BIN`)
- DVC (`pip install dvc dvc-ssh`) for pulling the database

### 1. Clone the repository

```bash
git clone https://github.com/haseeb-raza-13/mango-genome.git
cd mango-genome
```

### 2. Pull the BLAST database

The database files (268 MB) are tracked with DVC. Pull them from the remote:

```bash
# Configure your local SSH key for the DVC remote
dvc remote modify --local hostinger keyfile ~/.ssh/<your-key>

# Pull the data
dvc pull
```

This restores `mango-genome/backend/db/` with all 38 BLAST database files.

### 3. Backend

```bash
cd mango-genome/backend
python3.11 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Copy and edit the environment file
cp .env.example .env              # see Environment Variables section
uvicorn main:app --reload --port 8000
```

FastAPI docs available at [http://localhost:8000/docs](http://localhost:8000/docs).

### 4. Frontend

```bash
cd mango-genome/frontend
npm install

# Copy and edit the environment file
cp .env.local.example .env.local  # set FASTAPI_URL=http://localhost:8000
npm run dev
```

Frontend available at [http://localhost:3000](http://localhost:3000).

---

## Environment Variables

### Backend — `backend/.env`

```env
DB_PATH=/absolute/path/to/backend/db
DATA_PATH=/absolute/path/to/backend/db
BLAST_BIN=/path/to/blast/bin
CLUSTALO_BIN=/path/to/clustalo
CORS_ORIGINS=["http://localhost:3000"]
LOG_DIR=/path/to/backend/logs
OPENBLAS_NUM_THREADS=1
OMP_NUM_THREADS=1
MKL_NUM_THREADS=1
```

> `OPENBLAS_NUM_THREADS=1` is required on resource-limited servers (prevents numpy thread exhaustion). Safe to leave as-is on any machine.

### Frontend — `frontend/.env.local`

```env
FASTAPI_URL=http://localhost:8000
```

> This variable is server-side only (no `NEXT_PUBLIC_` prefix). The browser never contacts FastAPI directly.

---

## Database Setup (DVC)

BLAST database binary files are versioned with [DVC](https://dvc.org) and stored on the Hostinger server. The git repository stores only a pointer file (`backend/db.dvc`) containing the md5 hash and file count.

```bash
# Install DVC with SSH support
pip install dvc dvc-ssh

# Pull database files (requires SSH access to the DVC remote)
dvc pull

# After updating databases locally, push changes
dvc push
```

The DVC remote is configured in `.dvc/config`. Add your SSH key to `.dvc/config.local` (git-ignored):

```ini
['remote "hostinger"']
    keyfile = /path/to/your/ssh/key
```

---

## Deployment

The application runs on Hostinger Business Plan using Apache + Phusion Passenger.

### How it starts

1. A browser request hits Apache → Phusion Passenger starts the Node.js process
2. `server.js` (Next.js standalone server) spawns `uvicorn main:app --host 127.0.0.1 --port 8000` as a child process
3. Next.js API proxy routes forward requests to FastAPI at `http://127.0.0.1:8000`
4. FastAPI calls BLAST+ or Clustal Omega as subprocesses and returns JSON

### Triggering a restart after code changes

```bash
touch ~/domains/mangodb.cloud/nodejs/tmp/restart.txt
# Then visit the site in a browser — Passenger restarts Node.js on the next request
```

### Log files

```bash
# Node.js / Next.js output (includes backend spawn messages)
cat ~/domains/mangodb.cloud/nodejs/console.log

# FastAPI structured logs
cat ~/domains/mangodb.cloud/backend/logs/backend.log
```

---

## API Reference

All endpoints are internal — accessed through Next.js proxy routes, not directly from the browser.

### `GET /health`
Returns tool availability and configured paths.
```json
{
  "status": "ok",
  "blast_available": true,
  "clustalo_available": true,
  "blastn_path": "/path/to/blastn",
  "blastp_path": "/path/to/blastp",
  "clustalo_path": "/path/to/clustalo",
  "db_path": "/path/to/db",
  "data_path": "/path/to/db"
}
```

### `GET /blast/databases`
Returns available BLAST databases grouped by type.
```json
{
  "nucleotide": ["All Genomes", "CHINAZILLNUCLEOTIDE", "ISRAELKEITTNUCLEOTIDE", "MEXICOKENTNUCLEOTIDE", "PAKISTANLANGRA"],
  "protein":    ["All Proteomes", "CHINAZILLPROTEIN", "ISRAELKEITTPROTEIN", "MEXICOKENTPROTEIN"]
}
```

### `POST /blast`
Runs a BLAST search. Accepts `multipart/form-data`:

| Field | Type | Description |
|---|---|---|
| `sequence` | string | FASTA or raw sequence |
| `db` | string | Database name from `/blast/databases` |
| `blast_type` | string | `blastn` or `blastp` |
| `evalue` | float | E-value threshold (default `0.001`) |

Returns hits array, three base64 PNG plots, and a CSV string.

### `POST /msa`
Runs Clustal Omega alignment. Accepts `multipart/form-data`:

| Field | Type | Description |
|---|---|---|
| `sequences` | string | Multi-FASTA input |
| `files` | file[] | Optional: upload FASTA files |

Returns aligned FASTA, alignment stats, four base64 PNG plots, and a text report.

### `GET /files/{filename}`
Streams a FASTA file download. Filename must be in the server allowlist.

---

## License

MIT License — see [LICENSE](LICENSE) for details.

© 2026 Haseeb Raza
