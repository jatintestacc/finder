# 🚀 Job Hunter: AI-Powered Job Search Agent

Job Hunter is a production-ready AI agent that automates your job search. It accepts your resume, scrapes multiple job boards (LinkedIn, Indeed, etc.), scores every job against your profile using state-of-the-art AI, and delivers a richly formatted Excel report.

## ✨ Features

- **Multi-AI Support:** Works with Anthropic (Claude), Google (Gemini), Groq (Llama 3), DeepSeek, and Nvidia NIM.
- **Smart Failover:** Automatically detects which API key is available and switches if one fails.
- **Concurrent Scraping:** Scrapes LinkedIn, Indeed, Glassdoor, Naukri, and Wellfound simultaneously using Playwright.
- **ATS Scoring:** Computes a detailed match score (0-100) based on keywords, skills, experience, and education.
- **Actionable Advice:** Provides specific resume tips and interview topics for *every* job.
- **Rich Excel Output:** Color-coded results, "Perfect Match" highlights, and a comprehensive run summary.
- **GitHub Actions Ready:** Run it on a schedule or manually via the UI.

---

## 🛠️ Quick Start (Local)

1. **Clone & Install:**
   ```bash
   git clone <repo-url>
   cd job-hunter
   pip install -r requirements.txt
   playwright install chromium --with-deps
   ```

2. **Configure Environment:**
   Copy `.env.example` to `.env` and add at least ONE AI API key.
   ```bash
   cp .env.example .env
   ```

3. **Run the Agent:**
   ```bash
   python job_hunter.py --resume my_resume.pdf --role "Senior Backend Engineer" --location "Remote"
   ```

---

## 🤖 Which API Key Do I Need?

You only need **one** of the following. The script will use the first one it finds in this order:

| Provider | Model | Free Tier? | Sign Up |
| :--- | :--- | :--- | :--- |
| **Anthropic** | Claude 3.5 Sonnet | Limited | [Anthropic Console](https://console.anthropic.com) |
| **Gemini** | Gemini 1.5 Pro | Generous | [AI Studio](https://aistudio.google.com/app/apikey) |
| **Groq** | Llama 3.3 70B | Excellent | [Groq Cloud](https://console.groq.com) |
| **DeepSeek** | DeepSeek Chat | Affordable | [DeepSeek Platform](https://platform.deepseek.com) |
| **Nvidia** | Llama 3.1 70B | Credits | [Nvidia NIM](https://build.nvidia.com) |

---

## ☁️ Running on GitHub Actions

1. **Fork this repository.**
2. **Add Secrets:** Go to `Settings > Secrets and variables > Actions` and add:
   - `RESUME_B64`: Your resume base64 string (use `./scripts/encode_resume.sh` to get this).
   - `ANTHROPIC_API_KEY` (or any other provider key).
3. **Run Workflow:** Go to the `Actions` tab, select `Job Hunter AI`, and click `Run workflow`.

---

## 📊 Output Guide

The generated Excel file (`output/job_results_...xlsx`) contains:

1. **All Jobs:** Every scraped job with AI analysis, sorted by ATS score.
2. **Perfect Matches:** A filtered list of jobs where you scored 80% or higher.
3. **Run Summary:** A high-level dashboard showing job counts, top matches, and common skill gaps.

---

## 🤝 Notifications

If you set `SENDGRID_API_KEY` and `NOTIFY_EMAIL` in your `.env` or GitHub Secrets, Job Hunter will email you a beautiful HTML summary of the top 10 matches immediately after the run.

---

## 🔧 Troubleshooting

- **Scraping Blocked:** LinkedIn and Indeed have high bot protection. If local scraping fails, try running via GitHub Actions (different IP range) or use a proxy.
- **AI Error:** Ensure your API key is valid and you have credits. Check `job_hunter.log` for details.
- **Resume Parsing:** If your resume text isn't extracted well, try a simpler PDF layout.
