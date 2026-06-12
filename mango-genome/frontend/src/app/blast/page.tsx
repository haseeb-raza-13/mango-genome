"use client";
import { useEffect } from "react";
import { Dna, AlertCircle, CheckCircle } from "lucide-react";
import { useBlast } from "@/src/hooks/useBlast";
import BlastForm from "@/src/components/blast/BlastForm";
import BlastResultsTable from "@/src/components/blast/BlastResultsTable";
import BlastCharts from "@/src/components/blast/BlastCharts";

export default function BlastPage() {
  const { loading, result, error, databases, fetchDatabases, runBlast, reset } = useBlast();

  useEffect(() => {
    fetchDatabases();
  }, []);

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div>
        <div className="flex items-center gap-2 mb-1">
          <Dna size={20} className="text-accent" />
          <h1 className="text-xl font-bold text-white">BLAST Search</h1>
        </div>
        <p className="text-sm text-slate-400">
          Upload or paste your sequence to perform nucleotide (blastn) or protein (blastp) similarity search
          against pre-indexed mango genome databases.
        </p>
      </div>

      <div className="grid md:grid-cols-[380px_1fr] gap-6">
        {/* Form panel */}
        <div className="card">
          <BlastForm databases={databases} loading={loading} onSubmit={runBlast} />
        </div>

        {/* Results panel */}
        <div className="space-y-4">
          {loading && (
            <div className="card flex items-center gap-3 text-sm text-slate-400">
              <div className="w-4 h-4 border-2 border-accent border-t-transparent rounded-full animate-spin" />
              Running BLAST — this may take up to a few minutes for large databases…
            </div>
          )}

          {error && (
            <div className="card flex items-start gap-3 border-red-900/50 bg-red-950/20">
              <AlertCircle size={16} className="text-red-400 mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-sm font-semibold text-red-300">BLAST Error</p>
                <p className="text-xs text-red-400 mt-1 whitespace-pre-wrap">{error}</p>
              </div>
              <button onClick={reset} className="ml-auto text-xs text-slate-500 hover:text-white">Dismiss</button>
            </div>
          )}

          {result && (
            <>
              {/* Query stats */}
              <div className="card">
                <div className="flex items-center gap-2 mb-3">
                  <CheckCircle size={14} className="text-accent" />
                  <span className="text-sm font-semibold text-accent">BLAST completed</span>
                </div>
                <div className="flex gap-6 text-sm">
                  <div>
                    <span className="text-slate-500 text-xs">Query length</span>
                    <p className="text-white font-mono font-semibold">{result.query_length.toLocaleString()} bp</p>
                  </div>
                  <div>
                    <span className="text-slate-500 text-xs">GC content</span>
                    <p className="text-white font-semibold">{result.gc_content}%</p>
                  </div>
                  <div>
                    <span className="text-slate-500 text-xs">Total hits</span>
                    <p className="text-white font-semibold">{result.total_hits}</p>
                  </div>
                </div>
              </div>

              {result.hits.length === 0 ? (
                <div className="card text-center text-slate-400 text-sm py-8">
                  No hits found. Try a longer sequence or a different database.
                </div>
              ) : (
                <>
                  <div className="card">
                    <BlastResultsTable hits={result.hits} csvData={result.csv_data} />
                  </div>
                  {result.plots && (
                    <div className="card">
                      <BlastCharts plots={result.plots} />
                    </div>
                  )}
                </>
              )}
            </>
          )}

          {!loading && !result && !error && (
            <div className="card text-center text-slate-500 text-sm py-12 border-dashed">
              Submit a sequence to see BLAST results here.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
