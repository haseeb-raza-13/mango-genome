"use client";
import { useState } from "react";
import { ChevronDown, ChevronRight, Download } from "lucide-react";
import type { MsaPlots } from "@/src/types/msa";

interface PlotCardProps {
  title: string;
  src: string;
  filename: string;
}

function PlotCard({ title, src, filename }: PlotCardProps) {
  function download() {
    const a = document.createElement("a");
    a.href = `data:image/png;base64,${src}`;
    a.download = filename;
    a.click();
  }
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <h4 className="text-xs font-semibold text-slate-300">{title}</h4>
        <button onClick={download} className="btn-secondary flex items-center gap-1 text-xs py-0.5 px-2.5">
          <Download size={11} /> PNG
        </button>
      </div>
      <img src={`data:image/png;base64,${src}`} alt={title} className="w-full rounded border border-[#1a2a40]" />
    </div>
  );
}

export default function MsaCharts({ plots }: { plots: MsaPlots }) {
  const [dotsOpen, setDotsOpen] = useState(false);

  return (
    <div className="space-y-6">
      <PlotCard title="Pairwise Identity Heatmap" src={plots.identity_heatmap} filename="identity_heatmap.png" />
      <PlotCard title="Base / Amino Acid Frequencies" src={plots.base_frequency} filename="base_frequencies.png" />
      <PlotCard title="Pairwise Identity Distribution" src={plots.pairwise_distribution} filename="pairwise_distribution.png" />

      {plots.dot_plots.length > 0 && (
        <div>
          <button
            onClick={() => setDotsOpen((o) => !o)}
            className="flex items-center gap-2 text-sm font-semibold text-slate-300 hover:text-white mb-3"
          >
            {dotsOpen ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
            Dot Plots ({plots.dot_plots.length} pairs)
          </button>
          {dotsOpen && (
            <div className="grid sm:grid-cols-2 gap-4">
              {plots.dot_plots.map((dp) => (
                <PlotCard key={dp.label} title={dp.label} src={dp.image} filename={`dotplot_${dp.label.replace(/ /g, "_")}.png`} />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
