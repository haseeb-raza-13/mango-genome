import { Download, FileText, Archive } from "lucide-react";

const FASTA_FILES = [
  { name: "CHINAZILLNUCLEOTIDE.fasta", label: "China Zill — Nucleotide", type: "nucleotide" },
  { name: "CHINAZILLPROTEIN.fasta", label: "China Zill — Protein", type: "protein" },
  { name: "ISRAELKEITTNUCLEOTIDE.fasta", label: "Israel Keitt — Nucleotide", type: "nucleotide" },
  { name: "ISRAELKEITTPROTEIN.fasta", label: "Israel Keitt — Protein", type: "protein" },
  { name: "MEXICOKENTNUCLEOTIDE.fasta", label: "Mexico Kent — Nucleotide", type: "nucleotide" },
  { name: "MEXICOKENTPROTEIN.fasta", label: "Mexico Kent — Protein", type: "protein" },
  { name: "PAKISTANLANGRA.fasta", label: "Pakistan Langra — Nucleotide", type: "nucleotide" },
  { name: "Pakmod.fasta", label: "Pakistan Modi — Nucleotide", type: "nucleotide" },
  { name: "PAKPROT.fasta", label: "Pakistan Modi — Protein", type: "protein" },
];

const colorMap: Record<string, string> = {
  nucleotide: "bg-bio-blue/10 text-blue-300 border-blue-900/40",
  protein: "bg-bio-purple/10 text-purple-300 border-purple-900/40",
};

export default function Downloads() {
  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <div className="flex items-center gap-2 mb-1">
          <Download size={20} className="text-accent" />
          <h1 className="text-xl font-bold text-white">Downloads</h1>
        </div>
        <p className="text-sm text-slate-400">
          Download raw FASTA genome and proteome sequences for all mango cultivars.
        </p>
      </div>

      <div className="card space-y-2">
        {FASTA_FILES.map((f) => (
          <a
            key={f.name}
            href={`/api/downloads/${f.name}`}
            download={f.name}
            className="flex items-center gap-3 px-4 py-3 rounded-lg border border-[#1a2a40] hover:border-accent/50 hover:bg-accent/5 transition-all group"
          >
            <FileText size={16} className="text-slate-500 group-hover:text-accent flex-shrink-0" />
            <div className="flex-1">
              <p className="text-sm text-slate-200 group-hover:text-white transition-colors">{f.label}</p>
              <p className="text-xs text-slate-500 font-mono">{f.name}</p>
            </div>
            <span className={`text-xs px-2 py-0.5 rounded border ${colorMap[f.type]}`}>{f.type}</span>
            <Download size={13} className="text-slate-600 group-hover:text-accent" />
          </a>
        ))}

        <div className="pt-2 border-t border-[#1a2a40]">
          <a
            href="/api/downloads/nucleotide_protein_fasta.zip"
            download="nucleotide_protein_fasta.zip"
            className="flex items-center gap-3 px-4 py-3 rounded-lg border border-accent/30 bg-accent/5 hover:bg-accent/10 transition-all group"
          >
            <Archive size={16} className="text-accent flex-shrink-0" />
            <div className="flex-1">
              <p className="text-sm text-accent font-semibold">All Datasets (ZIP)</p>
              <p className="text-xs text-slate-500 font-mono">nucleotide_protein_fasta.zip</p>
            </div>
            <Download size={13} className="text-accent" />
          </a>
        </div>
      </div>

      <p className="text-xs text-slate-600 text-center">
        Files are served directly from the database server. Large files (&gt;40 MB) may take a moment to start downloading.
      </p>
    </div>
  );
}
