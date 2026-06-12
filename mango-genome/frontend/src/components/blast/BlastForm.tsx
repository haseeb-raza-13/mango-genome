"use client";
import { useCallback, useEffect, useState } from "react";
import { useDropzone } from "react-dropzone";
import { Upload, X, ChevronDown } from "lucide-react";
import clsx from "clsx";
import type { DatabaseList } from "@/src/types/blast";
import type { BlastFormState } from "@/src/hooks/useBlast";

interface Props {
  databases: DatabaseList | null;
  loading: boolean;
  onSubmit: (form: BlastFormState) => void;
}

export default function BlastForm({ databases, loading, onSubmit }: Props) {
  const [sequence, setSequence] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [blastType, setBlastType] = useState<"blastn" | "blastp">("blastn");
  const [database, setDatabase] = useState("");

  // Set default database when type or databases change
  useEffect(() => {
    if (!databases) return;
    const list = blastType === "blastn" ? databases.nucleotide : databases.protein;
    setDatabase(list[0] ?? "");
  }, [blastType, databases]);

  const onDrop = useCallback((accepted: File[]) => {
    if (accepted[0]) {
      setFile(accepted[0]);
      setSequence("");
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "text/plain": [".fasta", ".fa", ".txt"] },
    multiple: false,
  });

  const dbList = databases
    ? blastType === "blastn"
      ? databases.nucleotide
      : databases.protein
    : [];

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    onSubmit({ sequence, file, blastType, database });
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      {/* BLAST type */}
      <div className="flex gap-3">
        {(["blastn", "blastp"] as const).map((t) => (
          <button
            key={t}
            type="button"
            onClick={() => setBlastType(t)}
            className={clsx(
              "px-4 py-1.5 rounded-full text-sm font-semibold border transition-all",
              blastType === t
                ? "bg-accent text-[#060c1a] border-accent"
                : "border-[#1e3054] text-slate-400 hover:border-accent hover:text-accent"
            )}
          >
            {t}
          </button>
        ))}
      </div>

      {/* Sequence input */}
      <div>
        <label className="block text-xs text-slate-400 mb-1.5">Paste FASTA sequence</label>
        <textarea
          value={sequence}
          onChange={(e) => { setSequence(e.target.value); setFile(null); }}
          placeholder={">sequence_id\nATGCATGCATGC..."}
          rows={7}
          className="w-full bg-[#020810] border border-[#1e3054] rounded-lg p-3 font-mono text-xs text-[#a3e4d7] placeholder-slate-600 focus:outline-none focus:border-accent resize-y"
        />
      </div>

      <div className="flex items-center gap-3 text-xs text-slate-500">
        <div className="flex-1 border-t border-[#1e3054]" />
        <span>or upload file</span>
        <div className="flex-1 border-t border-[#1e3054]" />
      </div>

      {/* File drop zone */}
      <div
        {...getRootProps()}
        className={clsx(
          "border-2 border-dashed rounded-lg p-5 text-center cursor-pointer transition-all",
          isDragActive ? "border-accent bg-accent/5" : "border-[#1e3054] hover:border-accent/50"
        )}
      >
        <input {...getInputProps()} />
        {file ? (
          <div className="flex items-center justify-center gap-2 text-sm text-accent">
            <Upload size={14} />
            <span>{file.name}</span>
            <button
              type="button"
              onClick={(e) => { e.stopPropagation(); setFile(null); }}
              className="text-slate-400 hover:text-red-400"
            >
              <X size={14} />
            </button>
          </div>
        ) : (
          <div className="text-slate-500 text-sm">
            <Upload size={20} className="mx-auto mb-1 text-slate-600" />
            Drop a .fasta file here, or click to browse
          </div>
        )}
      </div>

      {/* Database selector */}
      <div>
        <label className="block text-xs text-slate-400 mb-1.5">Target database</label>
        <div className="relative">
          <select
            value={database}
            onChange={(e) => setDatabase(e.target.value)}
            className="w-full appearance-none bg-[#0d1528] border border-[#1e3054] rounded-lg px-3 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-accent pr-9"
          >
            {dbList.map((db) => (
              <option key={db} value={db}>{db}</option>
            ))}
            {dbList.length === 0 && <option value="">Loading databases...</option>}
          </select>
          <ChevronDown size={14} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 pointer-events-none" />
        </div>
      </div>

      <button
        type="submit"
        disabled={loading || (!sequence.trim() && !file) || !database}
        className="btn-accent w-full py-2.5 text-sm"
      >
        {loading ? "Running BLAST…" : "Run BLAST"}
      </button>
    </form>
  );
}
