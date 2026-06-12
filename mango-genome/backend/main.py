import os
# Limit OpenBLAS/NumPy threads to prevent CageFS thread exhaustion
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
import sys
import json
import logging
from logging.handlers import RotatingFileHandler

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

# ── Logging setup ──────────────────────────────────────────────────────────────
LOG_DIR = os.getenv("LOG_DIR", os.path.join(os.path.dirname(__file__), "logs"))
os.makedirs(LOG_DIR, exist_ok=True)

root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)

_fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

_file_handler = RotatingFileHandler(
    os.path.join(LOG_DIR, "backend.log"),
    maxBytes=10_000_000,
    backupCount=5,
    encoding="utf-8",
)
_file_handler.setFormatter(_fmt)
root_logger.addHandler(_file_handler)

_stdout_handler = logging.StreamHandler(sys.stdout)
_stdout_handler.setFormatter(_fmt)
root_logger.addHandler(_stdout_handler)

logger = logging.getLogger("mangodb")

# ── App ────────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Mango Genome Database API",
    description="Backend API for BLAST search, MSA, and genome data downloads",
    version="1.0.0",
)

CORS_ORIGINS = json.loads(os.getenv("CORS_ORIGINS", '["http://localhost:3000"]'))

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info("→ %s %s", request.method, request.url.path)
    response = await call_next(request)
    logger.info("← %s %s", response.status_code, request.url.path)
    return response


# ── Routers ────────────────────────────────────────────────────────────────────
from routers import blast, msa, files  # noqa: E402

app.include_router(blast.router, prefix="/blast", tags=["BLAST"])
app.include_router(msa.router, prefix="/msa", tags=["MSA"])
app.include_router(files.router, prefix="/files", tags=["Files"])


# ── Health check ───────────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"])
def health():
    import shutil

    blast_bin = os.getenv("BLAST_BIN", "")
    clustalo_bin = os.getenv("CLUSTALO_BIN", "clustalo")

    blastn_path = shutil.which("blastn", path=blast_bin or None) if blast_bin else shutil.which("blastn")
    blastp_path = shutil.which("blastp", path=blast_bin or None) if blast_bin else shutil.which("blastp")
    clustalo_path = shutil.which(clustalo_bin) if not os.path.isabs(clustalo_bin) else clustalo_bin

    result = {
        "status": "ok",
        "blast_available": bool(blastn_path and blastp_path),
        "clustalo_available": bool(clustalo_path),
        "blastn_path": blastn_path,
        "blastp_path": blastp_path,
        "clustalo_path": clustalo_path,
        "db_path": os.getenv("DB_PATH", "db"),
        "data_path": os.getenv("DATA_PATH", "data"),
    }
    logger.info("Health check: %s", result)
    return result


# ── Startup log ───────────────────────────────────────────────────────────────
@app.on_event("startup")
def on_startup():
    logger.info("=== Mango Genome Database API starting ===")
    logger.info("DB_PATH   : %s", os.getenv("DB_PATH", "db"))
    logger.info("DATA_PATH : %s", os.getenv("DATA_PATH", "data"))
    logger.info("BLAST_BIN : %s", os.getenv("BLAST_BIN", "(system PATH)"))
    logger.info("CLUSTALO  : %s", os.getenv("CLUSTALO_BIN", "clustalo"))
    logger.info("CORS      : %s", CORS_ORIGINS)
