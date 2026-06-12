import logging

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from schemas.msa import MsaResponse
from services.msa_service import run_msa

logger = logging.getLogger("mangodb.msa")
router = APIRouter()


@router.post("/align", response_model=MsaResponse)
async def msa_align(
    sequence: str = Form(default="", description="Multi-FASTA sequence text"),
    files: list[UploadFile] = File(default=[], description="One or more FASTA files"),
):
    # Collect input — files take priority over pasted text
    sequence_text = ""
    if files:
        parts = []
        for f in files:
            if f.filename:
                content = await f.read()
                parts.append(content.decode("utf-8", errors="replace"))
                logger.info("MSA input file: %s (%d bytes)", f.filename, len(content))
        sequence_text = "\n".join(parts)

    if not sequence_text and sequence.strip():
        sequence_text = sequence.strip()
        logger.info("MSA input from pasted text (%d chars)", len(sequence_text))

    if not sequence_text:
        raise HTTPException(
            status_code=422,
            detail="Provide FASTA sequences via text or upload FASTA files.",
        )

    try:
        result = run_msa(sequence_text)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except FileNotFoundError as exc:
        logger.error("MSA binary not found: %s", exc)
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        logger.exception("MSA failed unexpectedly")
        raise HTTPException(status_code=500, detail=f"MSA error: {exc}")

    return result
