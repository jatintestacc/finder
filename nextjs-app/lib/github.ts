export async function triggerWorkflow(inputs: Record<string, string>) {
  const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
  const GITHUB_OWNER = process.env.GITHUB_OWNER;
  const GITHUB_REPO = process.env.GITHUB_REPO;

  if (!GITHUB_TOKEN || !GITHUB_OWNER || !GITHUB_REPO) {
    console.error("Missing GitHub configuration:", { 
      token: !!GITHUB_TOKEN, 
      owner: GITHUB_OWNER, 
      repo: GITHUB_REPO 
    });
    return false;
  }

  const url = `https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/actions/workflows/job_hunt.yml/dispatches`;
  
  const res = await fetch(url, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${GITHUB_TOKEN}`,
      Accept: "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
      "User-Agent": "JobHunter-AI-Agent",
    },
    body: JSON.stringify({
      ref: "main",
      inputs,
    }),
  });

  if (res.status !== 204) {
    const text = await res.text();
    console.error(`GitHub Trigger Failed: ${res.status} - ${text}`);
  }

  return res.status === 204;
}

export async function getRecentWorkflowRun(sessionId?: string) {
  const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
  const GITHUB_OWNER = process.env.GITHUB_OWNER;
  const GITHUB_REPO = process.env.GITHUB_REPO;

  if (!GITHUB_TOKEN || !GITHUB_OWNER || !GITHUB_REPO) return null;

  const url = `https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/actions/runs?event=workflow_dispatch&per_page=20`;
  
  const res = await fetch(url, {
    headers: {
      Authorization: `Bearer ${GITHUB_TOKEN}`,
      Accept: "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
      "User-Agent": "JobHunter-AI-Agent",
    },
  });

  if (!res.ok) return null;
  const data = await res.json();

  const workflowRuns = Array.isArray(data.workflow_runs) ? data.workflow_runs : [];
  const now = new Date().getTime();
  const recentRuns = workflowRuns.filter((run: any) => {
    const runTime = new Date(run.created_at).getTime();
    const isRecent = (now - runTime) < 5 * 60 * 1000;
    const isTargetWorkflow = String(run.path || "").includes("job_hunt.yml");
    const isDispatch = run.event === "workflow_dispatch";
    return isRecent && isTargetWorkflow && isDispatch;
  });

  if (sessionId) {
    const matchedRun = recentRuns.find((run: any) =>
      String(run.display_title || "").includes(sessionId)
    );
    if (matchedRun) return matchedRun;
  }

  return recentRuns[0] || null;
}

export async function getWorkflowArtifacts(runId: string) {
  const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
  const GITHUB_OWNER = process.env.GITHUB_OWNER;
  const GITHUB_REPO = process.env.GITHUB_REPO;

  if (!GITHUB_TOKEN || !GITHUB_OWNER || !GITHUB_REPO) return [];

  const url = `https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/actions/runs/${runId}/artifacts`;
  
  const res = await fetch(url, {
    headers: {
      Authorization: `Bearer ${GITHUB_TOKEN}`,
      Accept: "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
      "User-Agent": "JobHunter-AI-Agent",
    },
  });

  if (!res.ok) return [];
  const data = await res.json();
  return data.artifacts;
}
