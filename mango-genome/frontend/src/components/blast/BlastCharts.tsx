"use client";
import { Download } from "lucide-react";
import type { BlastPlots } from "@/src/types/blast";

interface ChartProps {
  title: string;
  src: string;
  filename: string;
}

function PlotCard({ title, src, filename }: ChartProps) {
  function download() {
    const a = document.createElement("a");
    a.href = `data:image/png;base64,${src}`;
    a.download = filename;
    a.click();
  }

  return (
    <div className="card space-y-3">
      <div className="flex items-center justify-between">
        <h4 className="text-sm font-semibold text-slate-300">{title}</h4>
        <button onClick={download} className="btn-secondary flex items-center gap-1.5 text-xs py-1 px-3">
          <Download size={12} />
          PNG
        </button>
      </div>
      <img
        src={`data:image/png;base64,${src}`}
        alt={title}
        className="w-full rounded border border-[#1a2a40]"
      />
    </div>
  );
}

export default function BlastCharts({ plots }: { plots: BlastPlots }) {
  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold text-slate-300">Alignment Statistics</h3>
      <PlotCard title="% Identity Distribution" src={plots.identity_plot} filename="pct_identity.png" />
      <PlotCard title="-log₁₀(E-value) Distribution" src={plots.evalue_plot} filename="evalue_log10.png" />
      <PlotCard title="Bit Score Distribution" src={plots.bitscore_plot} filename="bit_score.png" />
    </div>
  );
}
