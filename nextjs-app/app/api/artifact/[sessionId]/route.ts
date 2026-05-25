import { getSession } from "../../../../lib/session";
import { NextRequest, NextResponse } from "next/server";

export async function GET(
  req: NextRequest,
  { params }: { params: { sessionId: string } }
) {
  try {
    const session = await getSession(params.sessionId);
    if (!session || !session.artifactZipUrl) {
      return NextResponse.json({ error: "Artifact not found" }, { status: 404 });
    }

    const response = await fetch(session.artifactZipUrl, {
      headers: {
        Authorization: `Bearer ${process.env.GITHUB_TOKEN}`,
      },
    });

    if (!response.ok) {
      return NextResponse.json({ error: "Failed to fetch artifact from GitHub" }, { status: 502 });
    }

    // Forward the stream
    return new NextResponse(response.body, {
      headers: {
        "Content-Disposition": `attachment; filename="job_results_${params.sessionId}.zip"`,
        "Content-Type": "application/zip",
      },
    });

  } catch (error) {
    console.error("Artifact Proxy Error:", error);
    return NextResponse.json({ error: "Internal Error" }, { status: 500 });
  }
}

export const maxDuration = 60;
