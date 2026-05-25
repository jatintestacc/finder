"use client";

import { useState, useEffect } from "react";
import { Loader2, ExternalLink, CheckCircle2, Clock } from "lucide-react";
import { useRouter } from "next/navigation";

interface StatusPollerProps {
  sessionId: string;
  initialStatus: string;
  workflowUrl?: string;
}

export default function StatusPoller({ sessionId, initialStatus, workflowUrl }: StatusPollerProps) {
  const [status, setStatus] = useState(initialStatus);
  const router = useRouter();

  useEffect(() => {
    if (status === "complete") {
      router.refresh();
      return;
    }

    const interval = setInterval(async () => {
      try {
        const res = await fetch(`/api/session?id=${sessionId}`);
        if (res.ok) {
          const data = await res.json();
          setStatus(data.status);
          if (data.status === "complete") {
            clearInterval(interval);
            router.refresh();
          }
        }
      } catch (err) {
        console.error("Polling error:", err);
      }
    }, 10000);

    return () => clearInterval(interval);
  }, [sessionId, status, router]);

  const steps = [
    { id: "idle", label: "Upload Resume", done: true },
    { id: "triggered", label: "Triggering AI Agent", done: ["running", "complete"].includes(status) },
    { id: "running", label: "Scraping & AI Analysis", done: status === "complete" },
    { id: "complete", label: "Ready", done: status === "complete" },
  ];

  return (
    <div className="bg-[#1A1A1A] p-12 rounded-3xl border border-gray-800 max-w-lg w-full text-center space-y-8 shadow-2xl">
      <div className="relative w-24 h-24 mx-auto">
        <div className="absolute inset-0 border-4 border-indigo-500/20 rounded-full"></div>
        <div className="absolute inset-0 border-4 border-indigo-500 rounded-full border-t-transparent animate-spin"></div>
        <div className="absolute inset-0 flex items-center justify-center">
          <Clock className="text-indigo-400" size={32} />
        </div>
      </div>

      <div className="space-y-2">
        <h2 className="text-2xl font-bold italic">Hunting for Jobs...</h2>
        <p className="text-gray-500 text-sm">Usually takes 5–15 minutes depending on volume.</p>
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

      {workflowUrl && (
        <a 
          href={workflowUrl} 
          target="_blank" 
          rel="noopener noreferrer"
          className="inline-flex items-center gap-2 text-indigo-400 hover:text-indigo-300 text-sm font-medium transition-colors"
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
