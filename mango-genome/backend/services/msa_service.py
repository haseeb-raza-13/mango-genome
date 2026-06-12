"""
MSA service — ported from MangoDB/msa.py with Streamlit calls removed.
Fixes the StringIO import bug (was at line 243 inside a nested function).
All plot functions return base64-encoded PNG strings.
"""
import logging
import os
import shutil
import subprocess
import tempfile
from collections import Counter
from io import StringIO
from itertools import combinations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from Bio import AlignIO
from Bio.Align import MultipleSeqAlignment

from schemas.msa import AlignmentStats, DotPlot, MsaPlots, MsaResponse
from utils.fasta_utils import validate_fasta
from utils.plot_utils import fig_to_base64

logger = logging.getLogger("mangodb.msa")


# ── Alignment computation ──────────────────────────────────────────────────────

def compute_alignment_stats(alignment: MultipleSeqAlignment) -> dict:
    stats: dict = {
        "alignment_length": alignment.get_alignment_length(),
        "pairwise_identities": [],
        "pairwise_gaps": [],
    }

    for rec1, rec2 in combinations(alignment, 2):
        matches = sum(a == b and a != "-" for a, b in zip(rec1.seq, rec2.seq))
        gaps = sum(a == "-" or b == "-" for a, b in zip(rec1.seq, rec2.seq))
        length = len(rec1.seq)
        stats["pairwise_identities"].append((matches / length) * 100)
        stats["pairwise_gaps"].append(gaps)

    if stats["pairwise_identities"]:
        stats["average_identity"] = sum(stats["pairwise_identities"]) / len(stats["pairwise_identities"])
        stats["average_gaps"] = sum(stats["pairwise_gaps"]) / len(stats["pairwise_gaps"])
    else:
        stats["average_identity"] = 0.0
        stats["average_gaps"] = 0.0

    return stats


def format_alignment_with_symbols(alignment: MultipleSeqAlignment, line_width: int = 60) -> str:
    """
    Formats alignment with '|' exact match, ':' similar base, ' ' mismatch/gap.
    Unchanged from msa.py.
    """
    purines = {"A", "G"}
    pyrimidines = {"C", "T"}

    output = ""
    alignment_len = alignment.get_alignment_length()

    for block_start in range(0, alignment_len, line_width):
        block_end = min(block_start + line_width, alignment_len)

        seq_lines = [
            f"Seq{i+1:<4} {str(record.seq[block_start:block_end])}"
            for i, record in enumerate(alignment)
        ]

        match_line = []
        for pos in range(block_start, block_end):
            column = [record.seq[pos] for record in alignment]
            if "-" in column:
                match_line.append(" ")
                continue
            if all(base == column[0] for base in column):
                match_line.append("|")
            elif all(base in purines for base in column) or all(base in pyrimidines for base in column):
                match_line.append(":")
            else:
                match_line.append(" ")

        output += "\n".join(seq_lines) + "\n"
        output += "    " + "    " + "".join(match_line) + "\n\n"

    return output


def generate_alignment_report(alignment: MultipleSeqAlignment, formatted: str, stats: dict) -> str:
    """Generate plain-text alignment report. Fixes the missing StringIO import from original."""
    buf = StringIO()
    buf.write("### Alignment Statistics\n")
    buf.write(f"Alignment Length: {stats['alignment_length']}\n")
    buf.write(f"Average Pairwise Identity: {stats['average_identity']:.2f}%\n")
    buf.write(f"Average Gaps per Pair: {stats['average_gaps']}\n")
    buf.write(f"Total Sequences: {len(alignment)}\n\n")
    buf.write("### Visual Alignment\n")
    buf.write(formatted)
    return buf.getvalue()


# ── Plots ──────────────────────────────────────────────────────────────────────

def plot_identity_heatmap(alignment: MultipleSeqAlignment) -> str:
    labels = [record.id for record in alignment]
    n = len(alignment)
    matrix = np.zeros((n, n))

    for i, rec1 in enumerate(alignment):
        for j, rec2 in enumerate(alignment):
            if i <= j:
                matches = sum(a == b and a != "-" for a, b in zip(rec1.seq, rec2.seq))
                identity = matches / len(rec1.seq) * 100
                matrix[i, j] = identity
                matrix[j, i] = identity

    df = pd.DataFrame(matrix, index=labels, columns=labels)
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(df, annot=True, fmt=".1f", cmap="viridis", ax=ax)
    ax.set_title("Pairwise Identity (%)")
    plt.tight_layout()
    return fig_to_base64(fig)


def plot_base_frequencies(alignment: MultipleSeqAlignment) -> str:
    base_counts: Counter = Counter()
    for record in alignment:
        base_counts.update(str(record.seq))

    bases = list(base_counts.keys())
    counts = [base_counts[base] for base in bases]

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(x=bases, y=counts, ax=ax)
    ax.set_title("Base / Amino Acid Frequencies")
    ax.set_xlabel("Base")
    ax.set_ylabel("Count")
    plt.tight_layout()
    return fig_to_base64(fig)


def plot_pairwise_distribution(stats: dict) -> str:
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(stats["pairwise_identities"], bins=10, color="teal", edgecolor="black")
    ax.set_title("Pairwise Identity Distribution")
    ax.set_xlabel("Identity (%)")
    ax.set_ylabel("Frequency")
    plt.tight_layout()
    return fig_to_base64(fig)


def plot_dotplot(seq1: str, seq2: str, window: int = 1) -> str:
    matches = [
        (i, j)
        for i in range(len(seq1) - window + 1)
        for j in range(len(seq2) - window + 1)
        if seq1[i : i + window] == seq2[j : j + window]
    ]
    x, y = zip(*matches) if matches else ([], [])
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.plot(x, y, "k.", markersize=1)
    ax.set_xlabel("Sequence 1")
    ax.set_ylabel("Sequence 2")
    ax.set_title("Dot Plot")
    plt.tight_layout()
    return fig_to_base64(fig)


# ── Main service function ──────────────────────────────────────────────────────

def _resolve_clustalo() -> str:
    clustalo_bin = os.getenv("CLUSTALO_BIN", "clustalo").strip()
    if os.path.isabs(clustalo_bin) and os.path.isfile(clustalo_bin):
        return clustalo_bin
    found = shutil.which(clustalo_bin)
    if found:
        return found
    raise FileNotFoundError(
        f"Clustal Omega binary '{clustalo_bin}' not found. "
        "Set CLUSTALO_BIN env var to the full path."
    )


def run_msa(sequence_text: str) -> MsaResponse:
    logger.info("MSA request: %d chars of sequence input", len(sequence_text))

    valid, err = validate_fasta(sequence_text)
    if not valid:
        raise ValueError(err)

    clustalo_bin = _resolve_clustalo()  # fail-fast before writing temp files

    in_fd, in_path = tempfile.mkstemp(suffix=".fasta", prefix="msa_in_")
    out_fd, out_path = tempfile.mkstemp(suffix=".fasta", prefix="msa_out_")

    try:
        with os.fdopen(in_fd, "w") as f:
            f.write(sequence_text)
        os.close(out_fd)

        cmd = [clustalo_bin, '-i', in_path, '-o', out_path, '--auto', '--force']
        logger.debug("Clustal Omega command: %s", ' '.join(cmd))

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode != 0:
            logger.error("clustalo failed (rc=%d): %s", result.returncode, result.stderr)
            raise ValueError(f"Clustal Omega alignment failed: {result.stderr}")
        if result.stderr:
            logger.debug("clustalo stderr: %s", result.stderr)

        alignment = AlignIO.read(out_path, "fasta")
        logger.info("MSA completed: %d sequences, length %d", len(alignment), alignment.get_alignment_length())

        with open(out_path) as f:
            aligned_fasta = f.read()

        formatted = format_alignment_with_symbols(alignment)
        stats_dict = compute_alignment_stats(alignment)
        report = generate_alignment_report(alignment, formatted, stats_dict)

        stats = AlignmentStats(
            alignment_length=stats_dict["alignment_length"],
            average_identity=stats_dict["average_identity"],
            average_gaps=stats_dict["average_gaps"],
            total_sequences=len(alignment),
            pairwise_identities=stats_dict["pairwise_identities"],
        )

        # Generate plots
        heatmap_b64 = plot_identity_heatmap(alignment)
        base_freq_b64 = plot_base_frequencies(alignment)
        pw_dist_b64 = plot_pairwise_distribution(stats_dict)

        dot_plots = [
            DotPlot(
                label=f"Seq{i+1} vs Seq{j+1}",
                image=plot_dotplot(str(alignment[i].seq), str(alignment[j].seq)),
            )
            for i, j in combinations(range(len(alignment)), 2)
        ]

        plots = MsaPlots(
            identity_heatmap=heatmap_b64,
            base_frequency=base_freq_b64,
            pairwise_distribution=pw_dist_b64,
            dot_plots=dot_plots,
        )

        return MsaResponse(
            aligned_fasta=aligned_fasta,
            formatted_alignment=formatted,
            stats=stats,
            plots=plots,
            report_text=report,
        )

    finally:
        for p in (in_path, out_path):
            try:
                os.unlink(p)
            except OSError:
                pass
