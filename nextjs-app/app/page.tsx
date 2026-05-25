import { getOrCreateSession } from "@/lib/session";
import { cookies } from "next/headers";
import ResumeUploader from "@/components/ResumeUploader";
import JobForm from "@/components/JobForm";
import SessionRecovery from "@/components/SessionRecovery";
import { Briefcase, Zap, Shield, Search } from "lucide-react";

export default async function LandingPage() {
  const cookieStore = cookies();
  const sessionId = cookieStore.get("jh_session")?.value;
  
  // session will be created/retrieved by middleware mostly, 
  // but we ensure it exists here for the server component logic.
  let session = null;
  if (sessionId) {
    session = await getOrCreateSession(sessionId);
  }

  return (
    <main className="container mx-auto px-4 py-12 min-h-screen flex flex-col justify-center">
      <div className="grid lg:grid-cols-2 gap-16 items-center">
        {/* Left Column: Hero Content */}
        <div className="space-y-8">
          <div>
            <h1 className="text-6xl font-extrabold tracking-tight mb-4 bg-gradient-to-r from-indigo-400 to-cyan-400 bg-clip-text text-transparent">
              Find Your Next Job <br /> with AI Precision.
            </h1>
            <p className="text-xl text-gray-400 max-w-lg">
              Upload your resume and let our AI agents hunt for the most relevant jobs, score them, and provide tailored advice.
            </p>
          </div>

          <div className="space-y-6">
            <FeatureItem 
              icon={<Search className="text-indigo-500" />}
              title="Global Scraping"
              description="LinkedIn, Indeed, and more — scanned concurrently in minutes."
            />
            <FeatureItem 
              icon={<Zap className="text-indigo-500" />}
              title="AI ATS Scoring"
              description="See exactly how you match every role with detailed match breakdowns."
            />
            <FeatureItem 
              icon={<Shield className="text-indigo-500" />}
              title="Private & Secure"
              description="Your resume is never stored. It's processed once and discarded."
            />
          </div>
        </div>

        {/* Right Column: Upload & Form Card */}
        <div className="bg-[#1A1A1A] p-8 rounded-2xl border border-gray-800 shadow-2xl space-y-8">
          <div className="space-y-2 text-center">
            <h2 className="text-2xl font-bold">Start Your Job Hunt</h2>
            <p className="text-gray-500 text-sm">Fill in the details below to begin the search.</p>
          </div>
          
          <JobForm sessionId={sessionId} />
        </div>
      </div>

      <div className="mt-24 border-t border-gray-900 pt-12 text-center">
        <SessionRecovery />
      </div>
    </main>
  );
}

function FeatureItem({ icon, title, description }: { icon: React.ReactNode, title: string, description: string }) {
  return (
    <div className="flex gap-4">
      <div className="bg-[#1A1A1A] p-3 rounded-lg border border-gray-800">
        {icon}
      </div>
      <div>
        <h3 className="font-semibold text-lg">{title}</h3>
        <p className="text-gray-500 text-sm">{description}</p>
      </div>
    </div>
  );
}
