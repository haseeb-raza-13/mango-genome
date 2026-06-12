import logging
import os

from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import FileResponse

logger = logging.getLogger("mangodb.files")
router = APIRouter()

# Allowlist of files that can be served — prevents directory traversal
ALLOWED_FILES = {
    "CHINAZILLNUCLEOTIDE.fasta",
    "CHINAZILLPROTEIN.fasta",
    "ISRAELKEITTNUCLEOTIDE.fasta",
    "ISRAELKEITTPROTEIN.fasta",
    "MEXICOKENTNUCLEOTIDE.fasta",
    "MEXICOKENTPROTEIN.fasta",
    "PAKISTANLANGRA.fasta",
    "Pakmod.fasta",
    "PAKPROT.fasta",
    "nucleotide_protein_fasta.zip",
}


@router.get("/{filename}")
def download_file(
    filename: str = Path(..., description="FASTA filename to download"),
):
    if filename not in ALLOWED_FILES:
        logger.warning("Rejected download attempt for disallowed file: %s", filename)
        raise HTTPException(status_code=404, detail="File not found.")

    data_dir = os.getenv("DATA_PATH", "data")
    file_path = os.path.join(data_dir, filename)

    if not os.path.isfile(file_path):
        logger.warning("File not on disk: %s", file_path)
        raise HTTPException(status_code=404, detail="File not found.")

    file_size = os.path.getsize(file_path)
    logger.info("Serving file: %s (%d bytes)", filename, file_size)

    media_type = "application/zip" if filename.endswith(".zip") else "text/plain"
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type=media_type,
    )


@router.get("/")
def list_files():
    """Return the list of available downloadable files."""
    data_dir = os.getenv("DATA_PATH", "data")
    available = []
    for fname in ALLOWED_FILES:
        fpath = os.path.join(data_dir, fname)
        if os.path.isfile(fpath):
            available.append({"filename": fname, "size_bytes": os.path.getsize(fpath)})
    return {"files": available}
