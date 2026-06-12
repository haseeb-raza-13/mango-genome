"use client";
import { useState } from "react";
import type { BlastResponse, DatabaseList } from "@/src/types/blast";

export interface BlastFormState {
  sequence: string;
  file: File | null;
  blastType: "blastn" | "blastp";
  database: string;
}

export function useBlast() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<BlastResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [databases, setDatabases] = useState<DatabaseList | null>(null);

  async function fetchDatabases() {
    try {
      const res = await fetch("/api/blast-databases");
      if (!res.ok) throw new Error(`Status ${res.status}`);
      const data: DatabaseList = await res.json();
      setDatabases(data);
      return data;
    } catch (err) {
      console.error("Failed to fetch databases", err);
      return null;
    }
  }

  async function runBlast(form: BlastFormState) {
    setLoading(true);
    setError(null);
    setResult(null);

    console.group("BLAST request");
    console.log("type:", form.blastType, "db:", form.database);
    console.log("sequence length:", form.sequence.length || (form.file ? form.file.size : 0));

    const fd = new FormData();
    fd.append("blast_type", form.blastType);
    fd.append("database", form.database);
    if (form.file) {
      fd.append("file", form.file);
    } else {
      fd.append("sequence", form.sequence);
    }

    try {
      const res = await fetch("/api/blast", { method: "POST", body: fd });
      const data = await res.json();
      console.log("response status:", res.status, "hits:", data?.total_hits);
      if (!res.ok) {
        setError(data?.detail ?? data?.error ?? "BLAST failed.");
      } else {
        setResult(data as BlastResponse);
      }
    } catch (err) {
      console.error("BLAST fetch error", err);
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

  return { loading, result, error, databases, fetchDatabases, runBlast, reset };
}
