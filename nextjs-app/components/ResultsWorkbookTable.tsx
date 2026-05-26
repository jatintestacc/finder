"use client";

import { useEffect, useState } from "react";
import JSZip from "jszip";
import * as XLSX from "xlsx";
import { AlertTriangle, FileSpreadsheet, Loader2 } from "lucide-react";

type WorkbookTableState = {
  headers: string[];
  rows: string[][];
  sheetName: string;
};

export default function ResultsWorkbookTable({ sessionId }: { sessionId: string }) {
  const [data, setData] = useState<WorkbookTableState | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function loadWorkbook() {
      try {
        setLoading(true);
        setError(null);

        const response = await fetch(`/api/artifact/${sessionId}`);
        if (!response.ok) {
          throw new Error("Could not fetch the Excel artifact.");
        }

        const zipBuffer = await response.arrayBuffer();
        const zip = await JSZip.loadAsync(zipBuffer);
        const workbookEntry = Object.values(zip.files).find((file) => file.name.toLowerCase().endsWith(".xlsx"));

        if (!workbookEntry) {
          throw new Error("No Excel file was found inside the artifact.");
        }

        const workbookBuffer = await workbookEntry.async("arraybuffer");
        const workbook = XLSX.read(workbookBuffer, { type: "array" });
        const firstSheetName = workbook.SheetNames[0];

        if (!firstSheetName) {
          throw new Error("The workbook did not contain any sheets.");
        }

        const sheet = workbook.Sheets[firstSheetName];
        const matrix = XLSX.utils.sheet_to_json<(string | number | boolean | null)[]>(sheet, {
          header: 1,
          raw: false,
          defval: "",
        });

        const [headerRow = [], ...bodyRows] = matrix;
        const headers = headerRow.map((cell, index) => String(cell || `Column ${index + 1}`));
        const rows = bodyRows
          .map((row) => headers.map((_, index) => String(row[index] ?? "")))
          .filter((row) => row.some((cell) => cell.trim().length > 0));

        if (!cancelled) {
          setData({
            headers,
            rows,
            sheetName: firstSheetName,
          });
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Failed to load Excel results.");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadWorkbook();

    return () => {
      cancelled = true;
    };
  }, [sessionId]);

  if (loading) {
    return (
      <div className="rounded-2xl border border-gray-800 bg-[#1A1A1A] p-8">
        <div className="flex items-center gap-3 text-gray-300">
          <Loader2 className="animate-spin text-indigo-400" size={18} />
          <span>Loading Excel rows...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-2xl border border-red-900/50 bg-red-950/30 p-8 text-red-100">
        <div className="flex items-start gap-3">
          <AlertTriangle className="mt-0.5 text-red-300" size={18} />
          <div className="space-y-2">
            <p className="font-semibold">Could not render the Excel table.</p>
            <p className="text-sm text-red-200/80">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  if (!data || data.headers.length === 0) {
    return (
      <div className="rounded-2xl border border-gray-800 bg-[#1A1A1A] p-8 text-gray-400">
        No tabular rows were found in the workbook.
      </div>
    );
  }

  return (
    <section className="rounded-2xl border border-gray-800 bg-[#1A1A1A] overflow-hidden">
      <div className="flex flex-col gap-3 border-b border-gray-800 bg-[#252525] px-6 py-5 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="flex items-center gap-2 font-bold">
            <FileSpreadsheet className="text-emerald-400" size={18} />
            Excel Results Table
          </h2>
          <p className="mt-1 text-sm text-gray-400">
            Showing sheet <span className="font-medium text-gray-200">{data.sheetName}</span> with {data.rows.length} rows.
          </p>
        </div>
        <div className="text-xs text-gray-500">
          Scroll horizontally to view all columns.
        </div>
      </div>

      <div className="max-h-[70vh] overflow-auto">
        <table className="min-w-full border-separate border-spacing-0 text-sm">
          <thead className="sticky top-0 z-10">
            <tr>
              {data.headers.map((header) => (
                <th
                  key={header}
                  className="border-b border-gray-800 bg-[#161616] px-4 py-3 text-left font-semibold text-gray-200"
                >
                  {header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.rows.map((row, rowIndex) => (
              <tr key={`${rowIndex}-${row[0] || "row"}`} className="odd:bg-white/[0.02]">
                {row.map((cell, columnIndex) => (
                  <td
                    key={`${rowIndex}-${columnIndex}`}
                    title={cell}
                    className="max-w-[280px] border-b border-gray-900 px-4 py-3 align-top text-gray-300"
                  >
                    <div className="whitespace-pre-wrap break-words">{cell || "-"}</div>
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
