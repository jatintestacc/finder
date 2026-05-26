import { getSession } from "../../../lib/session";
import StatusPoller from "../../../components/StatusPoller";
import SessionRecovery from "../../../components/SessionRecovery";
import ResultsWorkbookTable from "../../../components/ResultsWorkbookTable";
import { Download, CheckCircle, Clock, AlertTriangle, Search, Zap } from "lucide-react";

export default async function ResultsPage({ params }: { params: { sessionId: string } }) {
  const session = await getSession(params.sessionId);

  if (!session) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="bg-[#1A1A1A] p-8 rounded-2xl border border-gray-800 text-center space-y-4">
          <AlertTriangle className="mx-auto text-yellow-500 w-12 h-12" />
          <h1 className="text-2xl font-bold">Session Not Found</h1>
          <p className="text-gray-500">The results may have expired or the ID is incorrect.</p>
          <a href="/" className="inline-block bg-indigo-600 hover:bg-indigo-700 px-6 py-2 rounded-lg transition-colors font-medium">
            Go Home
          </a>
        </div>
      </div>
    );
  }

  if (session.status !== "complete") {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <StatusPoller sessionId={params.sessionId} initialStatus={session.status} workflowUrl={session.workflowRunUrl ?? undefined} />
      </div>
    );
  }

  return (
    <main className="container mx-auto px-4 py-16 max-w-7xl space-y-12">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
        <div>
          <h1 className="text-4xl font-bold mb-2">Your Job Hunt Results</h1>
          <p className="text-gray-400">Hunt for <span className="text-white font-semibold">{session.role}</span> in <span className="text-white font-semibold">{session.location}</span></p>
        </div>
        
        <a 
          href={`/api/artifact/${params.sessionId}`}
          className="bg-green-600 hover:bg-green-700 text-white px-8 py-4 rounded-xl font-bold flex items-center gap-3 transition-all transform hover:scale-105 shadow-lg shadow-green-900/20"
        >
          <Download size={20} />
          Download Excel Results
        </a>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard title="Total Found" value={session.jobCount || "..."} icon={<Search className="text-indigo-400" size={18} />} />
        <StatCard title="Perfect Matches" value={session.perfectMatches || "0"} icon={<CheckCircle className="text-green-400" size={18} />} />
        <StatCard title="Should Apply" value={session.shouldApply || "0"} icon={<Clock className="text-yellow-400" size={18} />} />
        <StatCard title="AI Provider" value={session.aiProvider || "N/A"} icon={<Zap className="text-cyan-400" size={18} />} />
      </div>

      <div className="bg-[#1A1A1A] border border-gray-800 rounded-2xl overflow-hidden">
        <div className="bg-[#252525] px-8 py-4 border-b border-gray-800">
          <h2 className="font-bold flex items-center gap-2 italic">
            <CheckCircle size={16} className="text-green-500" />
            Top AI Recommendation
          </h2>
        </div>
        <div className="p-8 space-y-4">
          {session.topMatch ? (
            <div className="space-y-2">
               <h3 className="text-2xl font-bold">{session.topMatch.title}</h3>
               <p className="text-gray-400 text-lg">{session.topMatch.company}</p>
               <div className="inline-block bg-green-900/30 text-green-400 px-3 py-1 rounded-full text-sm font-bold border border-green-800/50">
                  {session.topMatch.score}% ATS Match
               </div>
            </div>
          ) : (
            <p className="text-gray-500">Top match details will be visible in the Excel file.</p>
          )}
        </div>
      </div>

      <ResultsWorkbookTable sessionId={params.sessionId} />

      <div className="text-center space-y-2 p-8 border border-dashed border-gray-800 rounded-2xl bg-gray-900/30">
        <p className="text-gray-400">Save your session ID to access these results for the next 7 days:</p>
        <code className="bg-black px-4 py-2 rounded-lg text-indigo-400 font-mono text-lg block w-fit mx-auto border border-gray-800">
          {params.sessionId}
        </code>
      </div>

      <SessionRecovery />
    </main>
  );
}

function StatCard({ title, value, icon }: { title: string, value: string | number, icon: React.ReactNode }) {
  return (
    <div className="bg-[#1A1A1A] p-6 rounded-2xl border border-gray-800 space-y-4">
      <div className="flex justify-between items-center">
        <span className="text-gray-500 text-sm font-medium">{title}</span>
        {icon}
      </div>
      <div className="text-3xl font-bold">{value}</div>
    </div>
  );
}
