import { redis } from "./redis";

export interface SessionData {
  sessionId: string;
  createdAt: string;
  expiresAt: string;
  status: "idle" | "triggered" | "running" | "complete" | "failed";
  role: string;
  location: string;
  runId: string | null;
  workflowRunUrl: string | null;
  artifactZipUrl: string | null;
  artifactId: string | null;
  resultsReady: boolean;
  jobCount: number | null;
  perfectMatches: number | null;
  shouldApply: number | null;
  aiProvider: string | null;
  topMatch: { title: string; company: string; score: number } | null;
}

export async function getOrCreateSession(sessionId: string): Promise<SessionData> {
  const key = `session:${sessionId}`;
  const existing = await redis.get(key);

  if (existing) {
    return (typeof existing === "string" ? JSON.parse(existing) : existing) as SessionData;
  }

  const now = new Date();
  const expiry = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000);

  const newSession: SessionData = {
    sessionId,
    createdAt: now.toISOString(),
    expiresAt: expiry.toISOString(),
    status: "idle",
    role: "",
    location: "",
    runId: null,
    workflowRunUrl: null,
    artifactZipUrl: null,
    artifactId: null,
    resultsReady: false,
    jobCount: null,
    perfectMatches: null,
    shouldApply: null,
    aiProvider: null,
    topMatch: null,
  };

  await redis.set(key, JSON.stringify(newSession), { ex: 604800 });
  return newSession;
}

export async function getSession(sessionId: string): Promise<SessionData | null> {
  const key = `session:${sessionId}`;
  const data = await redis.get(key);
  if (!data) return null;
  return (typeof data === "string" ? JSON.parse(data) : data) as SessionData;
}

export async function updateSession(sessionId: string, updates: Partial<SessionData>) {
  const key = `session:${sessionId}`;
  const current = await getSession(sessionId);
  if (!current) return;

  const updated = { ...current, ...updates };
  await redis.set(key, JSON.stringify(updated), { ex: 604800 });
  return updated;
}
