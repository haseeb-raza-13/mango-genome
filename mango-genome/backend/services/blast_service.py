"""
BLAST search service — ported from MangoDB/blast.py with Streamlit calls removed.
Core subprocess logic is unchanged.
"""
import io
import logging
import os
import shutil
import subprocess
import tempfile

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from schemas.blast import BlastHit, BlastPlots, BlastResponse
from utils.fasta_utils import gc_content, extract_query_sequence
from utils.plot_utils import fig_to_base64

logger = logging.getLogger("mangodb.blast")

COLNAMES = [
    "Query ID", "Subject ID", "% Identity", "Alignment Length",
    "Mismatches", "Gap Openings", "Query Start", "Query End",
    "Subject Start", "Subject End", "E-value", "Bit Score",
]


def _resolve_db_path(db_dir: str, blast_type: str, db_choice: str) -> str:
    """
    Replicate the db_path logic from blast.py line 74.
    'All Genomes' / 'All Proteomes' → all_genomes / all_proteomes inside db_dir.
    Everything else uses the name as-is.
    """
    label = "All Genomes" if blast_type == "blastn" else "All Proteomes"
    if db_choice == label:
        folder_name = "all_genomes" if blast_type == "blastn" else "all_proteomes"
        return os.path.join(db_dir, folder_name)
    return os.path.join(db_dir, db_choice)


def _resolve_blast_binary(blast_type: str) -> str:
    blast_bin_dir = os.getenv("BLAST_BIN", "").strip()
    if blast_bin_dir:
        binary = os.path.join(blast_bin_dir, blast_type)
        if os.path.isfile(binary):
            return binary
    found = shutil.which(blast_type)
    if found:
        return found
    raise FileNotFoundError(
        f"'{blast_type}' binary not found. "
        "Set BLAST_BIN env var to the directory containing blastn/blastp."
    )


def get_available_databases(db_dir: str) -> dict:
    """
    Scan db_dir for .nsq and .psq index files and return available DB names.
    Mirrors the dynamic DB discovery logic from blast.py lines 30-38.
    """
    logger.debug("Scanning DB directory: %s", db_dir)
    try:
        db_files = os.listdir(db_dir)
    except FileNotFoundError:
        logger.error("DB directory not found: %s", db_dir)
        return {"nucleotide": [], "protein": []}

    nucleotide = sorted({f.split(".")[0] for f in db_files if f.endswith(".nsq")})
    protein = sorted({f.split(".")[0] for f in db_files if f.endswith(".psq")})

    # Ensure "All" options appear first
    if "all_genomes" in nucleotide:
        nucleotide.remove("all_genomes")
        nucleotide.insert(0, "All Genomes")
    if "all_proteomes" in protein:
        protein.remove("all_proteomes")
        protein.insert(0, "All Proteomes")

    logger.info("Available nucleotide DBs: %s", nucleotide)
    logger.info("Available protein DBs: %s", protein)
    return {"nucleotide": nucleotide, "protein": protein}


def run_blast(sequence_text: str, blast_type: str, db_choice: str) -> BlastResponse:
    """
    Run blastn or blastp against a pre-indexed database.
    Returns structured results with plots serialized as base64 PNGs.
    """
    db_dir = os.getenv("DB_PATH", "db")

    # Query stats
    query_seq = extract_query_sequence(sequence_text)
    seq_len = len(query_seq)
    gc = gc_content(query_seq) if blast_type == "blastn" else 0.0

    logger.info(
        "BLAST request: type=%s db=%s seq_len=%d gc=%.2f%%",
        blast_type, db_choice, seq_len, gc,
    )

    binary = _resolve_blast_binary(blast_type)
    db_path = _resolve_db_path(db_dir, blast_type, db_choice)

    query_fd, query_path = tempfile.mkstemp(suffix=".fasta", prefix="blast_query_")
    out_fd, out_path = tempfile.mkstemp(suffix=".txt", prefix="blast_out_")

    try:
        with os.fdopen(query_fd, "w") as qf:
            qf.write(sequence_text)
        os.close(out_fd)

        cmd = [
            binary,
            "-query", query_path,
            "-db", db_path,
            "-outfmt", "6",
            "-evalue", "1e-5",
            "-out", out_path,
        ]
        logger.debug("BLAST command: %s", " ".join(cmd))

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        if result.returncode != 0:
            logger.error(
                "BLAST failed (returncode=%d): %s", result.returncode, result.stderr
            )
            raise RuntimeError(f"BLAST error:\n{result.stderr}")

        with open(out_path) as f:
            output_text = f.read()

        if not output_text.strip():
            logger.info("BLAST returned no hits for db=%s", db_choice)
            return BlastResponse(
                query_length=seq_len,
                gc_content=gc,
                hits=[],
                total_hits=0,
                plots=None,
                csv_data="",
            )

        df = pd.read_csv(io.StringIO(output_text), sep="\t", names=COLNAMES)
        logger.info("BLAST completed: %d hits found", len(df))

        hits = [
            BlastHit(
                query_id=str(row["Query ID"]),
                subject_id=str(row["Subject ID"]),
                pct_identity=float(row["% Identity"]),
                alignment_length=int(row["Alignment Length"]),
                mismatches=int(row["Mismatches"]),
                gap_openings=int(row["Gap Openings"]),
                query_start=int(row["Query Start"]),
                query_end=int(row["Query End"]),
                subject_start=int(row["Subject Start"]),
                subject_end=int(row["Subject End"]),
                evalue=float(row["E-value"]),
                bit_score=float(row["Bit Score"]),
            )
            for _, row in df.iterrows()
        ]

        plots = _build_plots(df)
        csv_data = df.to_csv(index=False)

        return BlastResponse(
            query_length=seq_len,
            gc_content=gc,
            hits=hits,
            total_hits=len(hits),
            plots=plots,
            csv_data=csv_data,
        )

    finally:
        for p in (query_path, out_path):
            try:
                os.unlink(p)
            except OSError:
                pass


def _build_plots(df: pd.DataFrame) -> BlastPlots:
    logger.debug("Generating BLAST plots for %d hits", len(df))

    # 1. % Identity histogram
    fig1, ax1 = plt.subplots(figsize=(10, 5))
    ax1.hist(df["% Identity"], bins=20, color="skyblue", edgecolor="black")
    ax1.set_title("% Identity Distribution")
    ax1.set_xlabel("% Identity")
    ax1.set_ylabel("Count")
    plt.tight_layout()
    identity_b64 = fig_to_base64(fig1)

    # 2. E-value (-log10) histogram
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    evalues = df["E-value"].replace(0, 1e-180)
    ax2.hist(-np.log10(evalues), bins=20, color="salmon", edgecolor="black")
    ax2.set_title("Log10(E-value) Distribution")
    ax2.set_xlabel("-log10(E-value)")
    ax2.set_ylabel("Count")
    plt.tight_layout()
    evalue_b64 = fig_to_base64(fig2)

    # 3. Bit Score histogram
    fig3, ax3 = plt.subplots(figsize=(10, 5))
    ax3.hist(df["Bit Score"], bins=20, color="lightgreen", edgecolor="black")
    ax3.set_title("Bit Score Distribution")
    ax3.set_xlabel("Bit Score")
    ax3.set_ylabel("Count")
    plt.tight_layout()
    bitscore_b64 = fig_to_base64(fig3)

    return BlastPlots(
        identity_plot=identity_b64,
        evalue_plot=evalue_b64,
        bitscore_plot=bitscore_b64,
    )
