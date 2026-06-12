"use client";
import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { Upload, X } from "lucide-react";
import clsx from "clsx";
import type { MsaFormState } from "@/src/hooks/useMsa";

interface Props {
  loading: boolean;
  onSubmit: (form: MsaFormState) => void;
}

export default function MsaForm({ loading, onSubmit }: Props) {
  const [sequence, setSequence] = useState("");
  const [files, setFiles] = useState<File[]>([]);

  const onDrop = useCallback((accepted: File[]) => {
    setFiles((prev) => [...prev, ...accepted]);
    setSequence("");
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "text/plain": [".fasta", ".fa", ".txt"] },
    multiple: true,
  });

  function removeFile(idx: number) {
    setFiles((prev) => prev.filter((_, i) => i !== idx));
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    onSubmit({ sequence, files });
  }

  const canSubmit = sequence.trim().length > 0 || files.length > 0;

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      <div>
        <label className="block text-xs text-slate-400 mb-1.5">
          Paste multiple FASTA sequences
        </label>
        <textarea
          value={sequence}
          onChange={(e) => { setSequence(e.target.value); setFiles([]); }}
          placeholder={">seq1\nATGCATGC...\n>seq2\nGCATGCAT..."}
          rows={10}
          className="w-full bg-[#020810] border border-[#1e3054] rounded-lg p-3 font-mono text-xs text-[#a3e4d7] placeholder-slate-600 focus:outline-none focus:border-accent resize-y"
        />
      </div>

      <div className="flex items-center gap-3 text-xs text-slate-500">
        <div className="flex-1 border-t border-[#1e3054]" />
        <span>or upload files</span>
        <div className="flex-1 border-t border-[#1e3054]" />
      </div>

      <div
        {...getRootProps()}
        className={clsx(
          "border-2 border-dashed rounded-lg p-5 text-center cursor-pointer transition-all",
          isDragActive ? "border-accent bg-accent/5" : "border-[#1e3054] hover:border-accent/50"
        )}
      >
        <input {...getInputProps()} />
        <Upload size={20} className="mx-auto mb-1 text-slate-600" />
        <p className="text-slate-500 text-sm">Drop multiple .fasta files, or click to browse</p>
      </div>

      {files.length > 0 && (
        <ul className="space-y-1.5">
          {files.map((f, i) => (
            <li key={i} className="flex items-center gap-2 text-xs bg-[#0d1528] border border-[#1e3054] rounded px-3 py-1.5">
              <span className="flex-1 text-slate-300 truncate">{f.name}</span>
              <span className="text-slate-500">{(f.size / 1024).toFixed(1)} KB</span>
              <button type="button" onClick={() => removeFile(i)} className="text-slate-500 hover:text-red-400">
                <X size={12} />
              </button>
            </li>
          ))}
        </ul>
      )}

      <button
        type="submit"
        disabled={loading || !canSubmit}
        className="btn-accent w-full py-2.5 text-sm"
      >
        {loading ? "Running MSA…" : "Run Alignment"}
      </button>
    </form>
  );
}
