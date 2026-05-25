import { CheckCircle, Zap, Shield, Search, ExternalLink } from "lucide-react";

interface ResultsCardProps {
  title: string;
  company: string;
  score: number;
  location: string;
  salary: string;
  url: string;
}

export default function ResultsCard({ title, company, score, location, salary, url }: ResultsCardProps) {
  const getScoreColor = (s: number) => {
    if (s >= 80) return "text-green-400 bg-green-900/30 border-green-800/50";
    if (s >= 55) return "text-yellow-400 bg-yellow-900/30 border-yellow-800/50";
    return "text-red-400 bg-red-900/30 border-red-800/50";
  };

  return (
    <div className="bg-[#1A1A1A] border border-gray-800 rounded-2xl p-6 hover:border-gray-700 transition-all group">
      <div className="flex justify-between items-start gap-4 mb-4">
        <div>
          <h3 className="text-xl font-bold group-hover:text-indigo-400 transition-colors">{title}</h3>
          <p className="text-gray-400">{company}</p>
        </div>
        <div className={`px-3 py-1 rounded-full text-xs font-bold border ${getScoreColor(score)}`}>
          {score}% Match
        </div>
      </div>

      <div className="flex flex-wrap gap-4 text-sm text-gray-500 mb-6">
        <div className="flex items-center gap-1">
          <Search size={14} /> {location}
        </div>
        <div className="flex items-center gap-1">
          <Zap size={14} /> {salary}
        </div>
      </div>

      <a 
        href={url}
        target="_blank"
        rel="noopener noreferrer"
        className="w-full bg-[#252525] hover:bg-[#2D2D2D] text-white py-3 rounded-xl font-semibold flex items-center justify-center gap-2 transition-all border border-gray-800"
      >
        View Details <ExternalLink size={16} />
      </a>
    </div>
  );
}
