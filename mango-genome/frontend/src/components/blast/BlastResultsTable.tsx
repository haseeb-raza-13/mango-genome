"use client";
import {
  createColumnHelper,
  flexRender,
  getCoreRowModel,
  getSortedRowModel,
  useReactTable,
  type SortingState,
} from "@tanstack/react-table";
import { useState } from "react";
import { ArrowUpDown, Download } from "lucide-react";
import type { BlastHit } from "@/src/types/blast";

const col = createColumnHelper<BlastHit>();

const columns = [
  col.accessor("query_id", { header: "Query ID" }),
  col.accessor("subject_id", { header: "Subject ID" }),
  col.accessor("pct_identity", {
    header: "% Identity",
    cell: (i) => i.getValue().toFixed(2),
  }),
  col.accessor("alignment_length", { header: "Aln Len" }),
  col.accessor("mismatches", { header: "Mismatches" }),
  col.accessor("gap_openings", { header: "Gaps" }),
  col.accessor("query_start", { header: "Q.Start" }),
  col.accessor("query_end", { header: "Q.End" }),
  col.accessor("subject_start", { header: "S.Start" }),
  col.accessor("subject_end", { header: "S.End" }),
  col.accessor("evalue", {
    header: "E-value",
    cell: (i) => i.getValue().toExponential(2),
  }),
  col.accessor("bit_score", {
    header: "Bit Score",
    cell: (i) => i.getValue().toFixed(1),
  }),
];

interface Props {
  hits: BlastHit[];
  csvData: string;
}

export default function BlastResultsTable({ hits, csvData }: Props) {
  const [sorting, setSorting] = useState<SortingState>([]);

  const table = useReactTable({
    data: hits,
    columns,
    state: { sorting },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
  });

  function downloadCsv() {
    const blob = new Blob([csvData], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "blast_results.csv";
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-300">
          {hits.length} hit{hits.length !== 1 ? "s" : ""} found
        </h3>
        {csvData && (
          <button onClick={downloadCsv} className="btn-secondary flex items-center gap-2 text-xs py-1.5">
            <Download size={13} />
            Download CSV
          </button>
        )}
      </div>

      <div className="overflow-x-auto rounded-lg border border-[#1e3054]">
        <table className="min-w-full text-xs">
          <thead className="bg-[#0d1528] text-slate-400 uppercase tracking-wide">
            {table.getHeaderGroups().map((hg) => (
              <tr key={hg.id}>
                {hg.headers.map((header) => (
                  <th
                    key={header.id}
                    onClick={header.column.getToggleSortingHandler()}
                    className="px-3 py-2.5 text-left cursor-pointer select-none whitespace-nowrap hover:text-accent"
                  >
                    <span className="flex items-center gap-1">
                      {flexRender(header.column.columnDef.header, header.getContext())}
                      <ArrowUpDown size={10} className="text-slate-600" />
                    </span>
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody className="divide-y divide-[#1a2a40]">
            {table.getRowModel().rows.map((row) => (
              <tr key={row.id} className="hover:bg-[#0d1528] transition-colors">
                {row.getVisibleCells().map((cell) => (
                  <td key={cell.id} className="px-3 py-2 whitespace-nowrap text-slate-300 font-mono">
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
