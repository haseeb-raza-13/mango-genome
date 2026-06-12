import logging
import os

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from schemas.blast import BlastResponse, DatabaseListResponse
from services.blast_service import get_available_databases, run_blast
from utils.fasta_utils import validate_fasta

logger = logging.getLogger("mangodb.blast")
router = APIRouter()


@router.get("/databases", response_model=DatabaseListResponse)
def list_databases():
    db_dir = os.getenv("DB_PATH", "db")
    dbs = get_available_databases(db_dir)
    return DatabaseListResponse(nucleotide=dbs["nucleotide"], protein=dbs["protein"])


@router.post("/search", response_model=BlastResponse)
async def blast_search(
    blast_type: str = Form(..., description="blastn or blastp"),
    database: str = Form(..., description="Database name"),
    sequence: str = Form(default="", description="FASTA sequence text"),
    file: UploadFile = File(default=None, description="FASTA file upload"),
):
    # Resolve input — file takes priority over pasted text
    if file and file.filename:
        content = await file.read()
        sequence_text = content.decode("utf-8", errors="replace")
        logger.info("BLAST input from uploaded file: %s (%d bytes)", file.filename, len(content))
    elif sequence.strip():
        sequence_text = sequence.strip()
        logger.info("BLAST input from pasted text (%d chars)", len(sequence_text))
    else:
        raise HTTPException(status_code=422, detail="Provide a FASTA sequence or upload a file.")

    valid, err = validate_fasta(sequence_text)
    if not valid:
        raise HTTPException(status_code=422, detail=err)

    if blast_type not in ("blastn", "blastp"):
        raise HTTPException(status_code=422, detail="blast_type must be 'blastn' or 'blastp'.")

    try:
        result = run_blast(sequence_text, blast_type, database)
    except FileNotFoundError as exc:
        logger.error("Binary not found: %s", exc)
        raise HTTPException(status_code=503, detail=str(exc))
    except RuntimeError as exc:
        logger.error("BLAST runtime error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))

    return result
