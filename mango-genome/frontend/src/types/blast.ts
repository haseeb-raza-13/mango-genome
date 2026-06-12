export interface BlastHit {
  query_id: string;
  subject_id: string;
  pct_identity: number;
  alignment_length: number;
  mismatches: number;
  gap_openings: number;
  query_start: number;
  query_end: number;
  subject_start: number;
  subject_end: number;
  evalue: number;
  bit_score: number;
}

export interface BlastPlots {
  identity_plot: string;   // base64 PNG
  evalue_plot: string;
  bitscore_plot: string;
}

export interface BlastResponse {
  query_length: number;
  gc_content: number;
  hits: BlastHit[];
  total_hits: number;
  plots: BlastPlots | null;
  csv_data: string;
}

export interface DatabaseList {
  nucleotide: string[];
  protein: string[];
}
