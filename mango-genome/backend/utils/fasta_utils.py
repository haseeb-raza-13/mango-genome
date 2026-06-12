import logging

logger = logging.getLogger("mangodb.utils")


def gc_content(seq: str) -> float:
    """Return GC percentage of a nucleotide sequence (0–100)."""
    seq = seq.upper()
    if not seq:
        return 0.0
    gc = seq.count("G") + seq.count("C")
    return round(gc / len(seq) * 100, 2)


def parse_fasta_sequences(text: str) -> list[tuple[str, str]]:
    """
    Parse multi-FASTA text into list of (header, sequence) tuples.
    Returns empty list if text is blank or has no valid FASTA blocks.
    """
    sequences: list[tuple[str, str]] = []
    header = ""
    seq_parts: list[str] = []

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith(">"):
            if header:
                sequences.append((header, "".join(seq_parts)))
            header = line[1:].strip()
            seq_parts = []
        else:
            seq_parts.append(line)

    if header:
        sequences.append((header, "".join(seq_parts)))

    return sequences


def validate_fasta(text: str) -> tuple[bool, str]:
    """
    Validate that text contains at least one FASTA sequence.
    Returns (is_valid, error_message).
    """
    if not text or not text.strip():
        return False, "No sequence provided."

    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if not any(l.startswith(">") for l in lines):
        return False, "Input does not look like FASTA format (no '>' header found)."

    seqs = parse_fasta_sequences(text)
    if not seqs:
        return False, "Could not parse any sequences from the input."

    return True, ""


def extract_query_sequence(text: str) -> str:
    """Return concatenated sequence characters from FASTA text (first sequence)."""
    seqs = parse_fasta_sequences(text)
    if not seqs:
        return ""
    return seqs[0][1]
