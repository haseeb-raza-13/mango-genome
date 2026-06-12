export interface AlignmentStats {
  alignment_length: number;
  average_identity: number;
  average_gaps: number;
  total_sequences: number;
  pairwise_identities: number[];
}

export interface DotPlot {
  label: string;
  image: string; // base64 PNG
}

export interface MsaPlots {
  identity_heatmap: string;
  base_frequency: string;
  pairwise_distribution: string;
  dot_plots: DotPlot[];
}

export interface MsaResponse {
  aligned_fasta: string;
  formatted_alignment: string;
  stats: AlignmentStats;
  plots: MsaPlots | null;
  report_text: string;
}
