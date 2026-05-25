"use client";

import { useState } from "react";
import ResumeUploader from "./ResumeUploader";
import { Search, MapPin, Hash, BarChart3, ChevronRight, Loader2 } from "lucide-react";
import toast from "react-hot-toast";
import { useRouter } from "next/navigation";

interface JobFormProps {
  sessionId?: string;
}

export default function JobForm({ sessionId }: JobFormProps) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    role: "",
    location: "Remote",
    limit: 100,
    ats_threshold: 55,
    resume_b64: "",
    provider: "GEMINI",
    api_key: "",
    openai_base_url: "",
    boards: ["linkedin", "indeed", "glassdoor", "naukri", "wellfound"],
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.resume_b64) {
      toast.error("Please upload your resume first.");
      return;
    }
    if (!formData.api_key) {
      toast.error("Please provide an AI API Key.");
      return;
    }

    setLoading(true);
    try {
      const res = await fetch("/api/trigger", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...formData, sessionId }),
      });

      const data = await res.json();

      if (res.ok) {
        toast.success("Job hunt started!");
        router.push(`/results/${sessionId}`);
      } else {
        toast.error(data.error || "Failed to start job hunt.");
      }
    } catch (err) {
      toast.error("An error occurred. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <ResumeUploader onUpload={(b64) => setFormData({ ...formData, resume_b64: b64 })} />

      <div className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
           <select 
             className="w-full bg-[#252525] border border-gray-800 rounded-xl py-4 px-4 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all text-sm"
             value={formData.provider}
             onChange={(e) => setFormData({ ...formData, provider: e.target.value })}
           >
             <option value="ANTHROPIC">Anthropic (Claude)</option>
             <option value="GEMINI">Gemini (Google)</option>
             <option value="GROQ">Groq (Llama 3)</option>
             <option value="DEEPSEEK">DeepSeek</option>
             <option value="NVIDIA">Nvidia NIM</option>
           </select>
           <input
            required
            type="password"
            placeholder="AI API Key"
            className="w-full bg-[#252525] border border-gray-800 rounded-xl py-4 px-4 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all text-sm font-mono"
            value={formData.api_key}
            onChange={(e) => setFormData({ ...formData, api_key: e.target.value })}
          />
        </div>

        {["GROQ", "DEEPSEEK", "NVIDIA"].includes(formData.provider) && (
          <input
            type="text"
            placeholder="Custom Base URL (optional)"
            className="w-full bg-[#252525] border border-gray-800 rounded-xl py-4 px-4 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all text-sm"
            value={formData.openai_base_url}
            onChange={(e) => setFormData({ ...formData, openai_base_url: e.target.value })}
          />
        )}

        <div className="relative">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500" size={18} />
          <input
            required
            type="text"
            placeholder="Target Role (e.g. Backend Engineer)"
            className="w-full bg-[#252525] border border-gray-800 rounded-xl py-4 pl-12 pr-4 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
            value={formData.role}
            onChange={(e) => setFormData({ ...formData, role: e.target.value })}
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="relative">
            <MapPin className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500" size={18} />
            <input
              type="text"
              placeholder="Location"
              className="w-full bg-[#252525] border border-gray-800 rounded-xl py-4 pl-12 pr-4 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
              value={formData.location}
              onChange={(e) => setFormData({ ...formData, location: e.target.value })}
            />
          </div>
          <div className="relative">
            <Hash className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500" size={18} />
            <input
              type="number"
              max={200}
              placeholder="Limit"
              className="w-full bg-[#252525] border border-gray-800 rounded-xl py-4 pl-12 pr-4 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
              value={formData.limit}
              onChange={(e) => setFormData({ ...formData, limit: parseInt(e.target.value) })}
            />
          </div>
        </div>

        <div className="space-y-3 bg-[#252525] p-4 rounded-xl border border-gray-800">
          <div className="flex justify-between items-center text-sm">
            <label className="text-gray-400 flex items-center gap-2">
              <BarChart3 size={16} /> Min ATS Threshold
            </label>
            <span className="text-indigo-400 font-bold">{formData.ats_threshold}%</span>
          </div>
          <input
            type="range"
            min="0"
            max="100"
            className="w-full h-2 bg-gray-800 rounded-lg appearance-none cursor-pointer accent-indigo-500"
            value={formData.ats_threshold}
            onChange={(e) => setFormData({ ...formData, ats_threshold: parseInt(e.target.value) })}
          />
        </div>
      </div>

      <button
        disabled={loading}
        type="submit"
        className="w-full bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-600/50 text-white font-bold py-5 rounded-xl flex items-center justify-center gap-2 transition-all transform active:scale-[0.98] shadow-lg shadow-indigo-900/20"
      >
        {loading ? (
          <Loader2 className="animate-spin" />
        ) : (
          <>
            Hunt Jobs
            <ChevronRight size={20} />
          </>
        )}
      </button>
    </form>
  );
}
