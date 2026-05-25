import { verifySignature } from "@/lib/crypto";
import { redis } from "@/lib/redis";
import { updateSession } from "@/lib/session";
import { getWorkflowArtifacts } from "@/lib/github";
import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
  try {
    const rawBody = await req.text();
    const signature = req.headers.get("x-hub-signature-256") || "";

    if (!verifySignature(rawBody, signature)) {
      return NextResponse.json({ error: "Invalid signature" }, { status: 401 });
    }

    const payload = JSON.parse(rawBody);
    const event = req.headers.get("x-github-event");

    if (event !== "workflow_run") {
      return NextResponse.json({ message: "Ignored event" }, { status: 200 });
    }

    const { action, workflow_run } = payload;
    if (action !== "completed") {
      return NextResponse.json({ message: "In progress" }, { status: 200 });
    }

    const runId = String(workflow_run.id);
    const conclusion = workflow_run.conclusion; // success, failure, cancelled

    // Find session by runId
    const sessionId = await redis.get<string>(`runid:${runId}`);
    if (!sessionId) {
      return NextResponse.json({ error: "Session not found for run" }, { status: 404 });
    }

    if (conclusion === "success") {
      // Fetch artifact
      const artifacts = await getWorkflowArtifacts(runId);
      const excelArtifact = artifacts.find((a: any) => a.name === "jobs-excel");

      if (excelArtifact) {
        await updateSession(sessionId, {
          status: "complete",
          resultsReady: true,
          artifactZipUrl: excelArtifact.archive_download_url,
          artifactId: String(excelArtifact.id),
        });
      } else {
        await updateSession(sessionId, { status: "failed" });
      }
    } else {
      await updateSession(sessionId, { status: "failed" });
    }

    return NextResponse.json({ message: "Updated" }, { status: 200 });

  } catch (error) {
    console.error("Webhook Error:", error);
    return NextResponse.json({ error: "Internal Error" }, { status: 500 });
  }
}
