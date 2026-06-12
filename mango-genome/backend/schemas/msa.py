from typing import List, Optional
from pydantic import BaseModel


class AlignmentStats(BaseModel):
    alignment_length: int
    average_identity: float
    average_gaps: float
    total_sequences: int
    pairwise_identities: List[float]


class DotPlot(BaseModel):
    label: str
    image: str  # base64 PNG


class MsaPlots(BaseModel):
    identity_heatmap: str        # base64 PNG
    base_frequency: str          # base64 PNG
    pairwise_distribution: str   # base64 PNG
    dot_plots: List[DotPlot]


class MsaResponse(BaseModel):
    aligned_fasta: str
    formatted_alignment: str
    stats: AlignmentStats
    plots: Optional[MsaPlots] = None
    report_text: str
