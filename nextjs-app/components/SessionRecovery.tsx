"use client";

import { useState } from "react";
import { Search, Loader2 } from "lucide-react";
import toast from "react-hot-toast";
import { useRouter } from "next/navigation";

export default function SessionRecovery() {
  const [sessionId, setSessionId] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleRecover = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!sessionId.trim()) return;

    setLoading(true);
    try {
      const res = await fetch("/api/session", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sessionId }),
      });

      if (res.ok) {
        toast.success("Session recovered!");
        router.push(`/results/${sessionId}`);
      } else {
        toast.error("Invalid or expired session ID.");
      }
    } catch (err) {
      toast.error("An error occurred.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto space-y-4">
      <p className="text-gray-500 text-sm">Already have a session ID? Enter it here to recover your results:</p>
      <form onSubmit={handleRecover} className="flex gap-2">
        <input
          type="text"
          placeholder="Enter Session ID..."
          className="flex-1 bg-black border border-gray-800 rounded-lg px-4 py-2 focus:outline-none focus:ring-1 focus:ring-indigo-500 transition-all text-sm font-mono"
          value={sessionId}
          onChange={(e) => setSessionId(e.target.value)}
        />
        <button
          disabled={loading}
          type="submit"
          className="bg-gray-800 hover:bg-gray-700 text-white px-4 py-2 rounded-lg text-sm font-semibold transition-all flex items-center gap-2"
        >
          {loading ? <Loader2 className="animate-spin" size={16} /> : "Recover"}
        </button>
      </form>
    </div>
  );
}
