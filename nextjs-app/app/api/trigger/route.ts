import { getOrCreateSession, updateSession } from "../../../lib/session";
import { triggerWorkflow, getRecentWorkflowRun } from "../../../lib/github";
import { NextRequest, NextResponse } from "next/server";
import { redis } from "../../../lib/redis";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { sessionId, role, location, limit, ats_threshold, boards, resume_b64, provider, api_key, openai_base_url } = body;
    const cookieSessionId = req.cookies.get("jh_session")?.value;
    const resolvedSessionId = sessionId || cookieSessionId;

    if (!resolvedSessionId) {
      console.error("Trigger Error: No sessionId found in body or cookies");
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }
    if (!resume_b64) return NextResponse.json({ error: "Resume is required" }, { status: 400 });
    if (!role) return NextResponse.json({ error: "Role is required" }, { status: 400 });
    if (!api_key) return NextResponse.json({ error: "API Key is required" }, { status: 400 });

    await getOrCreateSession(resolvedSessionId);

    // Convert boards array to comma-separated string if needed
    const boardsString = Array.isArray(boards) ? boards.join(",") : (boards || "linkedin,indeed,glassdoor,naukri,wellfound");

    console.log(`Triggering workflow for role: ${role}, provider: ${provider}, boards: ${boardsString}`);
    console.log("Inputs being sent:", { 
      role, location, limit, ats_threshold, provider, 
      api_key: api_key ? "****" : "missing",
      openai_base_url, boards: boardsString,
      resume_len: resume_b64.length
    });

    // 1. Trigger GitHub Workflow
    const success = await triggerWorkflow({
      role: String(role || "auto"),
      location: String(location || "auto"),
      limit: String(limit || "100"),
      ats_threshold: String(ats_threshold || "55"),
      resume_b64,
      provider: String(provider || "GEMINI"),
      api_key: String(api_key),
      openai_base_url: String(openai_base_url || ""),
      boards: boardsString,
    });

    if (!success) {
      return NextResponse.json({ error: "Failed to trigger job hunt workflow" }, { status: 502 });
    }

    // 2. Wait a few seconds for GitHub to register the run
    await new Promise((resolve) => setTimeout(resolve, 4000));

    // 3. Find the run ID
    const run = await getRecentWorkflowRun();
    
    if (run) {
      // 4. Update Redis
      await updateSession(resolvedSessionId, {
        status: "running",
        runId: String(run.id),
        workflowRunUrl: run.html_url,
        role,
        location,
      });

      // Secondary index for webhook
      await redis.set(`runid:${run.id}`, resolvedSessionId, { ex: 604800 });

      return NextResponse.json({ 
        sessionId: resolvedSessionId, 
        runId: run.id, 
        workflowRunUrl: run.html_url 
      });
    }

    return NextResponse.json({ 
        sessionId: resolvedSessionId, 
        status: "triggered",
        message: "Workflow triggered, but run ID not yet available. It will update shortly."
    });

  } catch (error: any) {
    console.error("Trigger Error:", error);
    return NextResponse.json({ error: "Internal Server Error" }, { status: 500 });
  }
}
