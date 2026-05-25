# Job Hunter - Streamlit UI Quick Guide

A beautiful web interface for Job Hunter — no terminal needed!

## 🚀 Quick Start

### macOS / Linux:
```bash
bash scripts/run_streamlit.sh
```

### Windows:
```bash
scripts/run_streamlit.bat
```

### Manual:
```bash
pip install streamlit matplotlib plotly
streamlit run streamlit_app.py
```

Then open: **http://localhost:8501**

---

## 📱 Interface Overview

### Left Sidebar (Configuration)
- **Resume Upload** — Drag & drop your PDF or DOCX
- **Search Parameters** — Job role, location, max jobs
- **Job Boards** — Select which sites to search
- **Filters** — Minimum ATS score threshold
- **AI Provider** — Auto-detect or force a specific one

### Three Main Tabs

#### 1️⃣ 🔍 Run Search Tab
- Shows your search configuration
- Displays 4 key metrics (Target Role, Location, Max Jobs)
- **Start Job Hunt** button to begin
- Progress bar shows real-time updates
- Results summary when complete

#### 2️⃣ 📊 Results Tab
- Complete list of all analyzed jobs
- **Sort options**: ATS Score, Salary, Company Name
- **Filter options**: Perfect Match, Should Apply, Not Suitable
- **Job cards** with:
  - Job title, company, location
  - Match verdict (🟢🟡🔴)
  - ATS score (0-100)
  - Salary & remote type
  - "Apply" button
- **Expandable details** for each job:
  - Job info (type, level, industry, company size)
  - ATS breakdown (keyword overlap, skills match, etc.)
  - Job summary
  - Required skills vs matched skills
  - Skill gaps
  - Resume tips
  - Cover letter hints
  - Interview topics
  - Recruiter contact info

#### 3️⃣ 📈 Analytics Tab
- **Key statistics cards**: Perfect matches, Should apply, Remote jobs, Avg ATS score
- **ATS Score Distribution** chart
- **Match Verdict Breakdown** pie chart
- **Skill analysis**:
  - Top 5 required skills (across all jobs)
  - Top 5 skill gaps (what you need to learn)
- **Top insights**:
  - Total jobs analyzed
  - Average ATS score
  - Best matching job (with ATS score)
  - Highest salary

---

## 📖 How to Use - Step by Step

### Step 1: Upload Resume
1. In the left sidebar, click **"Upload your resume"**
2. Select your PDF or DOCX file
3. Wait for the ✓ confirmation

### Step 2: Configure Search
1. Enter your **Target job role** (e.g., "Senior Backend Engineer")
2. Enter your **Target location** (e.g., "Remote", "New York", "Bangalore")
3. Adjust **Max jobs to analyze** (start with 50, go up to 500 if you want more)

### Step 3: Select Job Boards
- Check the boxes for job boards you want searched
- Recommendation: LinkedIn, Indeed, Glassdoor (best coverage)
- At least one must be selected

### Step 4: Set Filters
1. **Minimum ATS score** — only show jobs with ATS ≥ this value
   - 0 = show all jobs
   - 50 = show average + above
   - 70 = show mostly good matches
   - 80 = show only excellent matches
2. **AI Provider** — leave as "Auto-detect" unless you have issues

### Step 5: Start Job Hunt
1. Click the big blue **🔍 Start Job Hunt** button
2. Watch the progress bar as:
   - Resume gets parsed (10%)
   - AI provider gets detected (15%)
   - Jobs get scraped from all boards (50%)
   - AI analyzes each job (90%)
   - Excel gets generated (100%)
3. This typically takes 2-10 minutes

### Step 6: Review Results
1. Click on the **📊 Results** tab
2. Sort or filter the jobs by:
   - ATS Score (highest first recommended)
   - Salary (highest first)
   - Company name
   - Match verdict (green/yellow/red)
3. For each job, you can:
   - See the job title, company, location
   - See the match verdict and ATS score
   - See salary (if disclosed)
   - Click "Apply" to open the job posting
   - Click **"Details"** to expand and see:
     - Why this job matches (keywords matched)
     - What you're missing (skill gaps)
     - Specific tips to improve your resume for this role
     - What to emphasize in your cover letter
     - Likely interview topics

### Step 7: View Analytics
1. Click on the **📈 Analytics** tab
2. See at a glance:
   - How many perfect matches you have
   - Distribution of ATS scores
   - Breakdown of match verdicts
   - Which skills are most in-demand
   - Which skills you need to acquire
   - Your best matching job

### Step 8: Download Results
- Excel file is automatically generated during the job hunt
- Check the **output/** folder for `job_results_YYYYMMDD_HHMMSS.xlsx`
- Gives you:
  - Sheet 1: All jobs (sortable, filterable)
  - Sheet 2: Perfect matches only (green sheet)
  - Sheet 3: Summary dashboard

---

## 🎨 Understanding the Colors

**In the Results Tab:**
- 🟢 **Green** = Perfect match (ATS ≥ 80)
  - Your resume strongly matches this job
  - High priority to apply
  
- 🟡 **Yellow** = Should apply (ATS 55–79)
  - Your resume matches reasonably well
  - You're qualified but not perfect fit
  - Still worth applying
  
- 🔴 **Red** = Not suitable (ATS < 55)
  - Your resume doesn't match well
  - Lower priority, but still contains useful insights

---

## 🎯 Tips for Best Results

1. **Resume Quality**
   - Use a well-formatted PDF or DOCX
   - Include all relevant skills and certifications
   - Use standard section headers (Skills, Experience, Education)

2. **Job Search**
   - Be specific with job title (e.g., "Senior Backend Engineer" vs "Engineer")
   - Location affects results (try "Remote" for maximum results)
   - Start with limit=50 for quick testing, then increase

3. **AI Provider**
   - All 5 providers work equally well
   - Groq is fastest (free)
   - Claude is most accurate (paid)
   - Start with whatever is easiest to get an API key for

4. **Interpreting Results**
   - ATS score is AI-generated, not definitive
   - Use the resume tips to customize your application
   - Green jobs are highest priority
   - Check the skill gaps to improve your resume

---

## 🐛 Troubleshooting

### Streamlit won't start
```
Error: streamlit: command not found
```
**Fix:** Install Streamlit: `pip install streamlit`

### Port 8501 is in use
```
Error: Address already in use
```
**Fix:** Use different port: `streamlit run streamlit_app.py --server.port 8502`

### Resume upload fails
- Check file size (< 20MB)
- Try converting to PDF
- Ensure file is not corrupted

### No jobs found
- Try a more general role name
- Change location
- Add more boards to search
- Increase job limit

### Progress bar stuck
- This is normal for large jobs counts
- Wait 5-10 minutes
- Check your internet connection

### AI provider error
- Make sure you have an API key in .env
- Check that the key is valid
- Try a different provider

---

## ⌨️ Keyboard Shortcuts

- **Ctrl+C** — Stop the Streamlit server
- **R** — Rerun the app (when focused on terminal)

---

## 💾 Output Files

After each job hunt, you get:

1. **job_results_YYYYMMDD_HHMMSS.xlsx** — Main Excel file with 3 sheets
2. **summary.json** — Statistics as JSON
3. **job_hunter.log** — Full execution logs

All saved in the `output/` folder.

---

## 🎓 Learning More

- **CLI Version**: See `README.md` for command-line usage
- **GitHub Actions**: Automate with scheduled runs
- **Custom Scripts**: Modify `streamlit_app.py` to add features

---

## 📞 Need Help?

1. Check `job_hunter.log` for detailed errors
2. Review the README.md troubleshooting section
3. Make sure all dependencies are installed: `pip install -r requirements.txt`

---

**Happy job hunting! 🎉**
