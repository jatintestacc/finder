"use client";

import { useState, useEffect } from "react";
import { ExternalLink, CheckCircle2, Clock, AlertTriangle } from "lucide-react";
import { useRouter } from "next/navigation";

interface StatusPollerProps {
  sessionId: string;
  initialStatus: string;
  workflowUrl?: string;
}

export default function StatusPoller({ sessionId, initialStatus, workflowUrl }: StatusPollerProps) {
  const [status, setStatus] = useState(initialStatus);
  const router = useRouter();

  const isFailed = status === "failed";
  const isComplete = status === "complete";
  const isTerminal = isFailed || isComplete;

  useEffect(() => {
    if (isTerminal) {
      if (isComplete) {
        router.refresh();
      }
      return;
    }

    const interval = setInterval(async () => {
      try {
        const res = await fetch(`/api/session?id=${sessionId}`);
        if (res.ok) {
          const data = await res.json();
          setStatus(data.status);
          if (["complete", "failed"].includes(data.status)) {
            clearInterval(interval);
            if (data.status === "complete") {
              router.refresh();
            }
          }
        }
      } catch (err) {
        console.error("Polling error:", err);
      }
    }, 10000);

    return () => clearInterval(interval);
  }, [sessionId, isTerminal, isComplete, router]);

  const steps = [
    { id: "idle", label: "Upload Resume", done: true },
    { id: "triggered", label: "Triggering AI Agent", done: ["triggered", "running", "complete", "failed"].includes(status) },
    { id: "running", label: "Scraping & AI Analysis", done: ["running", "complete", "failed"].includes(status) },
    { id: "complete", label: "Ready", done: status === "complete" },
  ];

  return (
    <div className="bg-[#1A1A1A] p-12 rounded-3xl border border-gray-800 max-w-lg w-full text-center space-y-8 shadow-2xl">
      <div className="relative w-24 h-24 mx-auto">
        <div className={`absolute inset-0 border-4 rounded-full ${isFailed ? "border-red-500/20" : "border-indigo-500/20"}`}></div>
        {!isFailed && (
          <div className="absolute inset-0 border-4 border-indigo-500 rounded-full border-t-transparent animate-spin"></div>
        )}
        <div className="absolute inset-0 flex items-center justify-center">
          {isFailed ? <AlertTriangle className="text-red-400" size={32} /> : <Clock className="text-indigo-400" size={32} />}
        </div>
      </div>

      <div className="space-y-2">
        <h2 className="text-2xl font-bold italic">{isFailed ? "Job Hunt Failed" : "Hunting for Jobs..."}</h2>
        <p className="text-gray-500 text-sm">
          {isFailed
            ? "The GitHub workflow finished with an error. Open the logs to inspect the failure and retry."
            : "Usually takes 5-15 minutes depending on volume."}
        </p>
      </div>

      <div className="space-y-4 text-left max-w-xs mx-auto">
        {steps.map((step, i) => (
          <div key={i} className="flex items-center gap-4">
            <div className={`w-6 h-6 rounded-full flex items-center justify-center border ${step.done ? "bg-indigo-500 border-indigo-500" : "border-gray-700 bg-gray-900"}`}>
              {step.done ? <CheckCircle2 size={14} className="text-white" /> : <div className="w-2 h-2 rounded-full bg-gray-700" />}
            </div>
            <span className={step.done ? "text-white font-medium" : "text-gray-600"}>{step.label}</span>
          </div>
        ))}
      </div>

      {isFailed && (
        <div className="rounded-2xl border border-red-900/60 bg-red-950/30 px-4 py-3 text-left text-sm text-red-200">
          The session status was updated to <code className="font-mono">failed</code>. You can retry the search after fixing the workflow issue.
        </div>
      )}

      {workflowUrl && (
        <a
          href={workflowUrl}
          target="_blank"
          rel="noopener noreferrer"
          className={`inline-flex items-center gap-2 text-sm font-medium transition-colors ${isFailed ? "text-red-300 hover:text-red-200" : "text-indigo-400 hover:text-indigo-300"}`}
        >
          Watch live logs on GitHub <ExternalLink size={14} />
        </a>
      )}

      <div className="pt-4 border-t border-gray-800">
        <p className="text-gray-500 text-xs mb-2">Save your session ID to return later:</p>
        <code className="text-indigo-400 font-mono text-xs bg-black px-3 py-1 rounded border border-gray-800">
          {sessionId}
        </code>
      </div>
    </div>
  );
}
