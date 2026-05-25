# 🖥️ Job Hunter Frontend

This is the Next.js 14 frontend for the Job Hunter AI agent. It provides a beautiful interface to upload your resume, configure your search, and retrieve results.

## 🛠️ Setup

### 1. Prerequisites
- Node.js 18+
- A GitHub Personal Access Token (PAT) with `repo` permissions.
- An Upstash Redis database (free tier).

### 2. Local Installation
```bash
cd nextjs-app
npm install
cp .env.local.example .env.local
```

### 3. GitHub Webhook Setup
To allow the frontend to receive results from GitHub Actions:
1. Go to your GitHub Repository -> **Settings** -> **Webhooks**.
2. Click **Add webhook**.
3. **Payload URL:** `https://your-vercel-domain.com/api/webhook`
4. **Content type:** `application/json`
5. **Secret:** Choose a strong secret and add it to your `.env.local` as `GITHUB_WEBHOOK_SECRET`.
6. **Events:** Select "Workflow runs".
7. Click **Add webhook**.

### 4. Development
```bash
npm run dev
```

## 🏗️ Architecture

1. **Upload:** Resume is converted to base64 in the browser and never stored on the server.
2. **Trigger:** The frontend calls the GitHub API to trigger a `workflow_dispatch` event, passing the resume and search parameters as inputs.
3. **Persistence:** Redis stores the mapping between GitHub `runId` and the user's `sessionId`.
4. **Notification:** When the workflow finishes, GitHub sends a POST request to `/api/webhook`.
5. **Retrieval:** The webhook updates the Redis session with the artifact download URL.
6. **Download:** The frontend proxies the artifact download from GitHub to keep your `GITHUB_TOKEN` secure.

## 🔒 Session Management
- Users are assigned a 7-day anonymous session via a secure cookie.
- If a user loses their cookie, they can recover their results using their **Session ID** shown on the results page.
