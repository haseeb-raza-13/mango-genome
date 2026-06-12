"use client";
import { useState } from "react";
import { Copy, Check, Download } from "lucide-react";

interface Props {
  alignedFasta: string;
  formattedAlignment: string;
  reportText: string;
}

export default function MsaAlignmentView({ alignedFasta, formattedAlignment, reportText }: Props) {
  const [tab, setTab] = useState<"visual" | "fasta">("visual");
  const [copied, setCopied] = useState(false);

  function copy() {
    navigator.clipboard.writeText(tab === "visual" ? formattedAlignment : alignedFasta).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  }

  function downloadFasta() {
    const blob = new Blob([alignedFasta], { type: "text/plain" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "aligned_sequences.fasta";
    a.click();
    URL.revokeObjectURL(a.href);
  }

  function downloadReport() {
    const blob = new Blob([reportText], { type: "text/plain" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "alignment_report.txt";
    a.click();
    URL.revokeObjectURL(a.href);
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between flex-wrap gap-2">
        <div className="flex gap-1 bg-[#020810] rounded-lg p-1">
          {(["visual", "fasta"] as const).map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={`px-3 py-1 rounded text-xs font-medium transition-all ${
                tab === t ? "bg-accent text-[#060c1a]" : "text-slate-400 hover:text-white"
              }`}
            >
              {t === "visual" ? "Visual Alignment" : "Aligned FASTA"}
            </button>
          ))}
        </div>
        <div className="flex gap-2">
          <button onClick={copy} className="btn-secondary flex items-center gap-1.5 text-xs py-1.5 px-3">
            {copied ? <Check size={12} className="text-accent" /> : <Copy size={12} />}
            {copied ? "Copied" : "Copy"}
          </button>
          <button onClick={downloadFasta} className="btn-secondary flex items-center gap-1.5 text-xs py-1.5 px-3">
            <Download size={12} />
            FASTA
          </button>
          <button onClick={downloadReport} className="btn-secondary flex items-center gap-1.5 text-xs py-1.5 px-3">
            <Download size={12} />
            Report
          </button>
        </div>
      </div>

      <pre className="sequence-display max-h-96 overflow-y-auto text-[11px] leading-[1.7]">
        {tab === "visual" ? formattedAlignment : alignedFasta}
      </pre>
    </div>
  );
}
