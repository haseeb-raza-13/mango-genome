from typing import Literal, List, Optional
from pydantic import BaseModel


class BlastHit(BaseModel):
    query_id: str
    subject_id: str
    pct_identity: float
    alignment_length: int
    mismatches: int
    gap_openings: int
    query_start: int
    query_end: int
    subject_start: int
    subject_end: int
    evalue: float
    bit_score: float


class BlastPlots(BaseModel):
    identity_plot: str   # base64 PNG
    evalue_plot: str     # base64 PNG
    bitscore_plot: str   # base64 PNG


class BlastResponse(BaseModel):
    query_length: int
    gc_content: float
    hits: List[BlastHit]
    total_hits: int
    plots: Optional[BlastPlots] = None
    csv_data: str


class DatabaseListResponse(BaseModel):
    nucleotide: List[str]
    protein: List[str]
