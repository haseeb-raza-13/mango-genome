"use client";
import { useState } from "react";
import type { MsaResponse } from "@/src/types/msa";

export interface MsaFormState {
  sequence: string;
  files: File[];
}

export function useMsa() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<MsaResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function runMsa(form: MsaFormState) {
    setLoading(true);
    setError(null);
    setResult(null);

    console.group("MSA request");
    console.log("sequences (chars):", form.sequence.length, "files:", form.files.length);

    const fd = new FormData();
    fd.append("sequence", form.sequence);
    form.files.forEach((f) => fd.append("files", f));

    try {
      const res = await fetch("/api/msa", { method: "POST", body: fd });
      const data = await res.json();
      console.log("response status:", res.status);
      if (!res.ok) {
        setError(data?.detail ?? data?.error ?? "MSA failed.");
      } else {
        setResult(data as MsaResponse);
      }
    } catch (err) {
      console.error("MSA fetch error", err);
      setError("Network error — could not reach the server.");
    } finally {
      setLoading(false);
      console.groupEnd();
    }
  }

  function reset() {
    setResult(null);
    setError(null);
  }

  return { loading, result, error, runMsa, reset };
}
