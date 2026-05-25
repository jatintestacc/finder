# Job Hunter 🎯

An AI-powered job hunting agent that scrapes the internet for relevant jobs, scores each job against your resume using AI, and outputs a richly formatted Excel file.

**Features:**
- ✅ Scrapes 5 major job boards (LinkedIn, Indeed, Glassdoor, Naukri, Wellfound)
- ✅ Accepts your resume (PDF or DOCX) and intelligently extracts skills, experience, education
- ✅ Uses 5 different AI providers (Claude, Gemini, Groq, DeepSeek, Nvidia) — pick any ONE
- ✅ Scores each job against your resume with AI-powered matching
- ✅ Outputs richly formatted Excel with 3 sheets: All Jobs, Perfect Matches, Run Summary
- ✅ Runs locally or via GitHub Actions (scheduled or manual trigger)
- ✅ Optional email notifications with top matches
- ✅ Async/await throughout for blazing performance
- ✅ Production-ready error handling and logging

---

## 🚀 Quick Start (Local)

### Option A: Web UI (Streamlit) — Recommended for Beginners

**Easiest way to run locally with a beautiful web interface:**

```bash
# 1. Clone and setup
git clone https://github.com/yourusername/job-hunter.git
cd job-hunter
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt
playwright install chromium --with-deps

# 3. Configure
cp .env.example .env
# Edit .env and add ONE AI provider key (see table below)

# 4. Launch Streamlit UI
streamlit run streamlit_app.py
```

Then:
- Open your browser to `http://localhost:8501`
- Upload your resume
- Configure search parameters
- Click "Start Job Hunt"
- View results with rich formatting and download Excel

**Or use the helper scripts:**
```bash
# macOS / Linux
bash scripts/run_streamlit.sh

# Windows
scripts/run_streamlit.bat
```

### Option B: Command Line — For Advanced Users

```bash
# 1-3. Same setup as above

# 4. Run directly from terminal
python job_hunter.py \
  --resume path/to/resume.pdf \
  --role "Software Engineer" \
  --location "Remote" \
  --limit 100
```

Output will be in `output/job_results_YYYYMMDD_HHMMSS.xlsx`

---

## � Web UI Features (Streamlit)

The Streamlit interface makes Job Hunter accessible to non-technical users:

### Features:
- 📄 **Resume Upload** — Drag & drop PDF or DOCX files
- ⚙️ **Configuration Panel** — Sidebar with all settings (role, location, boards, ATS threshold)
- 🔍 **Live Search** — Progress tracking during job scraping and AI analysis
- 📊 **Results Dashboard** — Interactive table with sorting and filtering
- 🎯 **Detailed Job Cards** — Click to expand full job details, ATS breakdown, resume tips
- 📈 **Analytics Tab** — Charts showing ATS distribution, match verdicts, skill analysis
- 💾 **Export** — Download Excel file directly
- 🤖 **Auto-Detect AI Provider** — No configuration needed if you have an API key in .env

### Interface Tabs:
1. **🔍 Run Search** — Start a new job hunt with your parameters
2. **📊 Results** — View all analyzed jobs with detailed information
3. **📈 Analytics** — Charts and statistics from your job hunt

### Step-by-Step Usage:

**1. Upload Resume**
   - Click "Upload your resume" in the sidebar
   - Select your PDF or DOCX file
   - Wait for confirmation message

**2. Configure Search**
   - Enter target job role (e.g., "Senior Backend Engineer")
   - Enter location (e.g., "Remote", "San Francisco", "Bangalore")
   - Adjust max jobs to analyze (10-500)

**3. Select Job Boards**
   - Check which job boards to search
   - Recommendation: Start with LinkedIn & Indeed for best coverage

**4. Set Filters & AI Provider**
   - Minimum ATS score (0-100) — only show jobs above this threshold
   - AI Provider — auto-detects or let you force a specific one

**5. Click "🔍 Start Job Hunt"**
   - Watch the progress bar as jobs are scraped
   - See live analysis updates
   - Wait for completion (2-10 minutes depending on job count)

**6. Review Results**
   - Switch to "📊 Results" tab
   - Click on any job to expand full details
   - See ATS scores, skill gaps, resume tips, and interview topics
   - Click "Apply" link to go directly to the job posting

**7. View Analytics**
   - Switch to "📈 Analytics" tab
   - See ATS score distribution chart
   - View match verdict breakdown (pie chart)
   - Check top required skills and skill gaps
   - Download the Excel file

---

### 1. Fork this repository to your GitHub account

### 2. Add your resume as a secret
```bash
# Encode your resume to base64
./scripts/encode_resume.sh path/to/resume.pdf

# Copy the output and create a GitHub secret:
# Settings → Secrets and variables → Actions → New repository secret
# Name: RESUME_B64
# Value: <paste the base64 string>
```

### 3. Add ONE AI provider key as a secret
```bash
# Settings → Secrets and variables → Actions → New repository secret
# Choose ONE of these names:
#   - ANTHROPIC_API_KEY (Claude)
#   - GEMINI_API_KEY (Google Gemini)
#   - GROQ_API_KEY (Groq)
#   - DEEPSEEK_API_KEY (DeepSeek)
#   - NVIDIA_API_KEY (Nvidia NIM)
```

### 4. Trigger the workflow
```bash
# Manual trigger:
# Go to Actions tab → Job Hunt → Run workflow → Fill inputs → Run

# Or set up automatic runs:
# (Already configured to run every Monday at 8:00 AM UTC)
```

### 5. Download results
- Results are attached as artifacts in the workflow run
- Excel file, logs, and JSON summary available for 30 days

---

## �️ CLI vs Web UI Comparison

| Feature | Web UI (Streamlit) | CLI (Command Line) |
|---------|-------------------|-------------------|
| **Setup** | Point & click, easy | Terminal commands |
| **Learning Curve** | ⭐ Beginner-friendly | ⭐⭐⭐ Advanced |
| **Visual Results** | ✅ Interactive dashboards | ✅ Excel file |
| **Progress Tracking** | ✅ Real-time progress bar | ✅ Log file |
| **Resume Upload** | ✅ Drag & drop | ✅ File path |
| **Customization** | ✅ GUI controls | ✅⭐⭐ Full control |
| **Automation** | ⭐ Manual only | ✅ Scriptable |
| **GitHub Actions** | ❌ N/A | ✅ Full support |
| **Scheduling** | ⭐ Manual only | ✅ Built-in cron |
| **Performance** | ✅ Same | ✅ Same |

**Recommendation:**
- **First time?** → Use **Web UI** (Streamlit) — easiest to get started
- **Want to schedule?** → Use **GitHub Actions** — runs automatically
- **Power user?** → Use **CLI** — maximum control & automation

---

## �📁 Project Structure

```
job-hunter/
├── job_hunter.py              # Main agent script
├── streamlit_app.py           # Web UI (Streamlit)
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules
├── README.md                 # This file
├── .github/
│   └── workflows/
│       └── job_hunt.yml      # GitHub Actions workflow
├── scripts/
│   ├── encode_resume.sh      # Resume encoder (macOS/Linux)
│   ├── encode_resume.bat     # Resume encoder (Windows)
│   ├── run_streamlit.sh      # Streamlit launcher (macOS/Linux)
│   └── run_streamlit.bat     # Streamlit launcher (Windows)
└── output/                   # Results directory (created automatically)
    ├── job_results_*.xlsx    # Excel output
    ├── summary.json          # Statistics in JSON
    └── job_hunter.log        # Execution logs
```

| Provider | Model | Free Tier | Speed | Cost | Signup Link |
|----------|-------|-----------|-------|------|------------|
| **Claude** (Anthropic) | claude-sonnet-4-20250514 | $5 credit | ⭐⭐⭐⭐ Fast | Pay-as-you-go | [console.anthropic.com](https://console.anthropic.com) |
| **Gemini** (Google) | gemini-1.5-pro | Unlimited | ⭐⭐⭐ Good | Free + paid | [aistudio.google.com](https://aistudio.google.com/app/apikey) |
| **Groq** | llama-3.3-70b-versatile | Unlimited | ⭐⭐⭐⭐⭐ Fastest | Free tier | [console.groq.com](https://console.groq.com) |
| **DeepSeek** | deepseek-chat | $5 credit | ⭐⭐⭐⭐ Fast | Cheap ($0.07 /1M tokens) | [platform.deepseek.com](https://platform.deepseek.com) |
| **Nvidia NIM** | llama-3.1-70b-instruct | 1000 requests/day | ⭐⭐⭐ Good | Free tier | [build.nvidia.com](https://build.nvidia.com) |

**Recommendation for beginners:** Start with **Groq** (free, unlimited, fastest). If you hit rate limits, switch to **Gemini** (unlimited free tier).

---

## 📋 CLI Usage

```bash
python job_hunter.py \
  --resume <path>              # ✅ REQUIRED: PDF or DOCX file
  --role <string>              # ✅ REQUIRED: Target job role (e.g., "Backend Engineer")
  --location <string>          # Default: "Remote"
  --limit <int>                # Default: 100 (max jobs to process)
  --ats-threshold <int>        # Default: 0 (min ATS score to include in output)
  --boards <csv list>          # Default: all (linkedin,indeed,glassdoor,naukri,wellfound)
  --output-dir <path>          # Default: ./output
  --provider <name>            # Force a specific AI provider, skip auto-detect
  --log-level <level>          # Default: INFO (DEBUG|INFO|WARNING)
```

### Examples

```bash
# Find all remote backend engineering roles, scored by AI
python job_hunter.py --resume resume.pdf --role "Backend Engineer" --location "Remote"

# Find on-site data science roles in New York, only include high-matching jobs
python job_hunter.py \
  --resume resume.pdf \
  --role "Data Scientist" \
  --location "New York" \
  --ats-threshold 70

# Use only Groq provider, process up to 50 jobs, save to custom folder
python job_hunter.py \
  --resume resume.pdf \
  --role "DevOps Engineer" \
  --limit 50 \
  --provider groq \
  --output-dir /tmp/jobs
```

---

## 📊 Output Files

### Excel File: `job_results_YYYYMMDD_HHMMSS.xlsx`

Three richly formatted sheets:

#### Sheet 1: "All Jobs"
- All analyzed jobs sorted by ATS score (highest first)
- 30+ columns with rich job details
- Color-coded rows:
  - 🟢 **Green** = Perfect match (ATS ≥ 80)
  - 🟡 **Yellow** = Should apply (ATS 55–79)
  - 🔴 **Red** = Not suitable (ATS < 55)
- Auto-filter enabled on all columns
- Frozen header row
- Text wrapping on long fields

#### Sheet 2: "Perfect Matches"
- Only jobs with ATS score ≥ 80
- Summary box showing count, average score, run date
- Same formatting as Sheet 1
- Green tab for easy identification

#### Sheet 3: "Run Summary"
- Dashboard with key statistics
- Job counts and breakdown
- Top match, salary info, remote opportunities
- Skill gap analysis
- Beautiful styled formatting
- Blue tab

### JSON File: `output/summary.json`
Statistics in JSON format for programmatic access.

### Logs: `job_hunter.log`
Full execution logs with timestamps and details.

---

## 🛠️ Environment Variables

### Required (choose ONE):
- `ANTHROPIC_API_KEY` - Claude API key
- `GEMINI_API_KEY` - Google Gemini API key
- `GROQ_API_KEY` - Groq API key
- `DEEPSEEK_API_KEY` - DeepSeek API key
- `NVIDIA_API_KEY` - Nvidia NIM API key

### Optional:
- `SENDGRID_API_KEY` - For email notifications
- `NOTIFY_EMAIL` - Email address to receive notifications
- `LOG_LEVEL` - Logging level (DEBUG|INFO|WARNING)

---

## 🔍 How It Works

### 1. Resume Parsing
- Accepts PDF or DOCX files
- AI-assisted extraction of:
  - Skills
  - Years of experience
  - Education & certifications
  - Job titles held
  - Tech keywords
- Falls back to regex if AI parsing fails

### 2. Job Scraping
- Scrapes 5 job boards concurrently
- Extracts job title, company, location, description, URL
- De-duplicates by company + title
- Uses random delays and rotating user-agents to avoid detection
- Respects robots.txt

### 3. AI Analysis (per job)
- Single AI call per job for efficiency
- Extracts:
  - Job details (title, location, remote type, experience level, industry, company size)
  - Compensation (salary range, currency, visa sponsorship)
  - Content (summary, skills, responsibilities, nice-to-haves)
  - **ATS Score** (0–100) based on:
    - Keyword overlap (40%)
    - Skills match (30%)
    - Experience alignment (20%)
    - Education match (10%)
  - Match verdict (Perfect, Should Apply, Not Suitable)
  - Actionable advice (resume tips, cover letter hints, interview topics)

### 4. Excel Generation
- Richly formatted with colors, fonts, borders
- Auto-filter and frozen headers
- Sorted by ATS score descending
- Perfect for sharing with recruiters or tracking applications

### 5. Provider Auto-Detection
- Checks environment for ONE of 5 AI provider keys in priority order
- Tests with a health check (ping)
- Falls back to next provider if current fails
- Same functionality from all providers — you just need one key!

---

## 🐛 Troubleshooting

### "No AI provider keys found"
- **Problem:** None of the 5 provider env vars are set
- **Solution:** 
  1. Copy `.env.example` to `.env`
  2. Add at least ONE API key
  3. For GitHub Actions, add the key as a secret

### "Playwright installation failed"
- **Problem:** Browser installation failed
- **Solution:** Run `playwright install chromium --with-deps`
- **On Ubuntu/Debian:** May need `sudo apt-get install -y libnss3 libxss1`

### "Resume parsing failed"
- **Problem:** PDF/DOCX file could not be parsed
- **Solution:**
  1. Ensure file is not corrupted
  2. Try converting DOCX to PDF (sometimes easier to parse)
  3. Check file permissions

### "LinkedIn/Indeed scraping not working"
- **Problem:** Website structure changed or blocking automated access
- **Solution:**
  1. Manually check if the website loads in browser
  2. Check `job_hunter.log` for specific errors
  3. Try a different board (`--boards indeed,glassdoor`)

### "ATS score seems wrong"
- **Problem:** AI scoring doesn't match your expectations
- **Solution:**
  1. The AI uses keyword matching + skill overlap + experience + education
  2. A lower score might mean your resume skills don't match the JD keywords
  3. Consider the AI's "resume_tips" column for specific improvements

### "Script runs but no output file"
- **Problem:** No jobs found or all filtered out
- **Solution:**
  1. Check logs: `cat job_hunter.log`
  2. Try higher `--limit` value
  3. Try different `--location`
  4. Lower `--ats-threshold` to include more jobs
  5. Check internet connection

### Streamlit UI issues

**"Streamlit not found" or import error**
- **Solution:** Make sure you've installed requirements: `pip install streamlit matplotlib plotly`

**"Port 8501 already in use"**
- **Solution:** Run on a different port: `streamlit run streamlit_app.py --server.port 8502`

**"Resume upload not working"**
- **Solution:** 
  1. Check file size (should be < 20MB)
  2. Ensure file is not corrupted
  3. Try a different format (PDF vs DOCX)

**"Progress bar stuck or slow"**
- **Solution:**
  1. This is normal — job scraping and AI analysis takes time
  2. Start with `--limit 20` for testing
  3. Check internet connection
  4. Try with fewer job boards selected

**"Analytics not showing"**
- **Solution:** Make sure you've completed a full job hunt first (click "Start Job Hunt")

### GitHub Actions workflow fails
- **Problem:** Workflow errors in logs
- **Solution:**
  1. Check `RESUME_B64` secret is set and valid base64
  2. Check AI provider key is set (e.g., `ANTHROPIC_API_KEY`)
  3. Wait a moment and re-run (temporary API issues)
  4. Check workflow logs for detailed error messages

---

## 📝 Output Format Reference

### Resume Profile
```python
ResumeProfile(
    full_text="...",              # Original resume text
    skills=["Python", "Go", ...], # Extracted technical skills
    experience_years=5,           # Calculated experience
    education=["B.S. CS", ...],   # Education details
    job_titles=["Engineer", ...], # Previous job titles
    certifications=["AWS", ...],  # Certifications
    tech_keywords=[...]           # Technical keywords found
)
```

### Job Result
```python
JobResult(
    # Identification
    job_title="Senior Backend Engineer",
    company="TechCorp",
    location="San Francisco, USA",
    remote_type="Hybrid",
    employment_type="Full-time",
    experience_level="Senior",
    industry="FinTech",
    company_size="201-500",
    
    # Compensation
    salary_min=150000,
    salary_max=200000,
    salary_currency="USD",
    salary_display="$150K–$200K / yr",
    visa_sponsorship="Yes",
    
    # ATS Scoring
    ats_score=85,                 # 0–100
    match_verdict="Perfect match", # Perfect/Should/Not
    keywords_matched=["Python", "Kubernetes", ...],
    keywords_missing=["Rust", ...],
    skill_gaps=["Learn Rust", ...],
    
    # Advice
    resume_tips=["Add Kubernetes to skills", ...],
    cover_letter_hint="Emphasize distributed systems experience",
    interview_topics=["System design", ...],
    
    # Contact
    contact_email="hr@techcorp.com",
    apply_url="https://...",
    
    # Meta
    source_board="LinkedIn",
    ai_provider_used="claude",
    run_timestamp="2024-01-15T10:30:00"
)
```

---

## 🚀 Performance Tips

1. **Start with fewer jobs:**
   ```bash
   python job_hunter.py --resume resume.pdf --role "Engineer" --limit 20
   ```
   Increase `--limit` as you get comfortable.

2. **Use faster AI provider:**
   - Groq is fastest (free tier available)
   - Great for initial test runs

3. **Filter to good matches:**
   ```bash
   python job_hunter.py --resume resume.pdf --role "Engineer" --ats-threshold 60
   ```
   This reduces Excel processing time.

4. **Run on GitHub Actions:**
   - Offloads work from your computer
   - Can be scheduled automatically
   - Artifacts stored for 30 days

---

## 🔐 Security & Privacy

- ✅ Resume is parsed locally (never sent to 3rd parties unless via AI provider)
- ✅ All API keys stored in `.env` file (local) or GitHub Secrets (CI)
- ✅ `.gitignore` prevents .env and resume files from being committed
- ✅ GitHub Actions: secrets never printed in logs or artifacts
- ✅ Resume file auto-deleted after workflow completion
- ✅ No data persistence — each run is isolated

---

## 📚 Example Workflow

```bash
# 1. Set up
git clone https://github.com/yourusername/job-hunter.git
cd job-hunter
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium --with-deps

# 2. Configure
cp .env.example .env
# Edit .env and add your API key

# 3. Run for a specific role
python job_hunter.py \
  --resume ~/Documents/my_resume.pdf \
  --role "Senior Backend Engineer" \
  --location "San Francisco" \
  --limit 50

# 4. Open Excel file
open output/job_results_20240115_143022.xlsx

# 5. Review results
# - Look at "Perfect Matches" sheet first (green rows)
# - Check "resume_tips" for personalization suggestions
# - Use "apply_url" to apply directly
```

---

## 🤝 Contributing

Found a bug? Have a feature request?

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

MIT License — see LICENSE file for details

---

## 🙏 Acknowledgments

Built with:
- **Playwright** — Web scraping
- **BeautifulSoup4** — HTML parsing
- **Anthropic Claude, Google Gemini, Groq, DeepSeek, Nvidia** — AI scoring
- **OpenPyXL** — Excel generation
- **aiohttp** — Async HTTP client
- **pdfplumber** — PDF parsing

---

## 💬 Support

Have questions? Found an issue?

1. Check the **Troubleshooting** section above
2. Review `job_hunter.log` for detailed error messages
3. Run with `--log-level DEBUG` for verbose output
4. Open an issue on GitHub with:
   - Error message
   - Your command
   - Relevant log lines
   - Your environment (OS, Python version)

---

## 📞 Contact

- **GitHub Issues:** [report a bug](../../issues)
- **Discussions:** [ask a question](../../discussions)

---

**Happy job hunting! 🎉**
#   f i n d e r  
 