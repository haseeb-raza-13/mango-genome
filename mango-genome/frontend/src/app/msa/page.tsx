"use client";
import { AlignJustify, AlertCircle, CheckCircle } from "lucide-react";
import { useMsa } from "@/src/hooks/useMsa";
import MsaForm from "@/src/components/msa/MsaForm";
import MsaAlignmentView from "@/src/components/msa/MsaAlignmentView";
import MsaCharts from "@/src/components/msa/MsaCharts";

export default function MsaPage() {
  const { loading, result, error, runMsa, reset } = useMsa();

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div>
        <div className="flex items-center gap-2 mb-1">
          <AlignJustify size={20} className="text-accent" />
          <h1 className="text-xl font-bold text-white">Multiple Sequence Alignment</h1>
        </div>
        <p className="text-sm text-slate-400">
          Align multiple FASTA sequences using Clustal Omega. View the alignment, identity heatmap, and download results.
        </p>
      </div>

      <div className="grid md:grid-cols-[380px_1fr] gap-6">
        <div className="card">
          <MsaForm loading={loading} onSubmit={runMsa} />
        </div>

        <div className="space-y-4">
          {loading && (
            <div className="card flex items-center gap-3 text-sm text-slate-400">
              <div className="w-4 h-4 border-2 border-accent border-t-transparent rounded-full animate-spin" />
              Running Clustal Omega alignment…
            </div>
          )}

          {error && (
            <div className="card flex items-start gap-3 border-red-900/50 bg-red-950/20">
              <AlertCircle size={16} className="text-red-400 mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-sm font-semibold text-red-300">MSA Error</p>
                <p className="text-xs text-red-400 mt-1 whitespace-pre-wrap">{error}</p>
              </div>
              <button onClick={reset} className="ml-auto text-xs text-slate-500 hover:text-white">Dismiss</button>
            </div>
          )}

          {result && (
            <>
              {/* Stats */}
              <div className="card">
                <div className="flex items-center gap-2 mb-3">
                  <CheckCircle size={14} className="text-accent" />
                  <span className="text-sm font-semibold text-accent">Alignment completed</span>
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">
                  {[
                    ["Sequences", result.stats.total_sequences],
                    ["Alignment Length", result.stats.alignment_length.toLocaleString()],
                    ["Avg Identity", `${result.stats.average_identity.toFixed(2)}%`],
                    ["Avg Gaps/Pair", result.stats.average_gaps.toFixed(1)],
                  ].map(([label, val]) => (
                    <div key={String(label)}>
                      <span className="text-slate-500 text-xs">{label}</span>
                      <p className="text-white font-semibold">{val}</p>
                    </div>
                  ))}
                </div>
              </div>

              <div className="card">
                <MsaAlignmentView
                  alignedFasta={result.aligned_fasta}
                  formattedAlignment={result.formatted_alignment}
                  reportText={result.report_text}
                />
              </div>

              {result.plots && (
                <div className="card">
                  <h3 className="text-sm font-semibold text-slate-300 mb-4">Visualizations</h3>
                  <MsaCharts plots={result.plots} />
                </div>
              )}
            </>
          )}

          {!loading && !result && !error && (
            <div className="card text-center text-slate-500 text-sm py-12 border-dashed">
              Submit sequences to see alignment results here.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
