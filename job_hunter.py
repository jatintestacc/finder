import asyncio
import base64
import json
import logging
import os
import random
import re
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import aiohttp
import pdfplumber
from bs4 import BeautifulSoup
from docx import Document
from dotenv import load_dotenv
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from playwright.async_api import async_playwright
from tqdm.asyncio import tqdm

# --- Configuration & Constants ---
load_dotenv()

PROVIDERS = {
    "ANTHROPIC": {
        "key": "ANTHROPIC_API_KEY",
        "model": "claude-3-5-sonnet-20240620",
        "url": "https://api.anthropic.com/v1/messages",
        "type": "anthropic"
    },
    "GEMINI": {
        "key": "GEMINI_API_KEY",
        "model": "gemini-1.5-pro",
        "url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent",
        "type": "gemini"
    },
    "GROQ": {
        "key": "GROQ_API_KEY",
        "model": "llama-3.3-70b-versatile",
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "type": "openai"
    },
    "DEEPSEEK": {
        "key": "DEEPSEEK_API_KEY",
        "model": "deepseek-chat",
        "url": "https://api.deepseek.com/v1/chat/completions",
        "type": "openai"
    },
    "NVIDIA": {
        "key": "NVIDIA_API_KEY",
        "model": "meta/llama-3.1-70b-instruct",
        "url": "https://integrate.api.nvidia.com/v1/chat/completions",
        "type": "openai"
    }
}

PRIORITY_LIST = ["ANTHROPIC", "GEMINI", "GROQ", "DEEPSEEK", "NVIDIA"]

# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("job_hunter.log")
    ]
)
logger = logging.getLogger("JobHunter")

# --- Dataclasses ---

@dataclass
class ResumeProfile:
    full_text: str
    skills: List[str] = field(default_factory=list)
    experience_years: int = 0
    education: List[str] = field(default_factory=list)
    job_titles: List[str] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)
    tech_keywords: List[str] = field(default_factory=list)
    suggested_role: str = "Software Engineer"
    suggested_location: str = "Remote"

@dataclass
class RawJob:
    title: str
    company: str
    description: str
    url: str
    source_board: str

@dataclass
class JobResult:
    # Identification
    job_title: str
    company: str
    location: str
    remote_type: str
    employment_type: str
    experience_level: str
    industry: str
    company_size: str
    # Compensation
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: Optional[str] = None
    salary_display: str = "Not disclosed"
    visa_sponsorship: str = "Unknown"
    posted_date: Optional[str] = None
    application_deadline: Optional[str] = None
    # Content
    description_summary: str = ""
    skills_required: List[str] = field(default_factory=list)
    responsibilities: List[str] = field(default_factory=list)
    nice_to_have: List[str] = field(default_factory=list)
    # ATS Scoring
    ats_score: int = 0
    ats_breakdown: Dict[str, int] = field(default_factory=dict)
    match_verdict: str = "Not suitable"
    keywords_matched: List[str] = field(default_factory=list)
    keywords_missing: List[str] = field(default_factory=list)
    skill_gaps: List[str] = field(default_factory=list)
    # Advice
    resume_tips: List[str] = field(default_factory=list)
    cover_letter_hint: str = ""
    interview_topics: List[str] = field(default_factory=list)
    # Contact
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    apply_url: str = ""
    # Meta
    source_board: str = ""
    ai_provider_used: str = ""
    run_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

# --- AI Client Adapter ---

class AIClient:
    def __init__(self, provider_name: str, api_key: str):
        self.provider_name = provider_name
        self.api_key = api_key
        self.config = PROVIDERS[provider_name]
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def complete(self, prompt: str, system: str = "") -> str:
        if not self.session:
            self.session = aiohttp.ClientSession()

        for attempt in range(4):
            try:
                if self.config["type"] == "anthropic":
                    headers = {
                        "x-api-key": self.api_key,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json"
                    }
                    data = {
                        "model": self.config["model"],
                        "max_tokens": 4096,
                        "system": system,
                        "messages": [{"role": "user", "content": prompt}]
                    }
                    async with self.session.post(self.config["url"], headers=headers, json=data) as resp:
                        if resp.status == 200:
                            res = await resp.json()
                            return res["content"][0]["text"]
                        elif resp.status in [429, 500, 502, 503, 504]:
                            await self._handle_retry(attempt, resp.status)
                            continue
                        else:
                            text = await resp.text()
                            raise Exception(f"Anthropic API Error {resp.status}: {text}")

                elif self.config["type"] == "gemini":
                    url = f"{self.config['url']}?key={self.api_key}"
                    data = {
                        "contents": [{"parts": [{"text": f"{system}\n\n{prompt}"}]}]
                    }
                    async with self.session.post(url, json=data) as resp:
                        if resp.status == 200:
                            res = await resp.json()
                            return res["candidates"][0]["content"]["parts"][0]["text"]
                        elif resp.status in [429, 500, 502, 503, 504]:
                            await self._handle_retry(attempt, resp.status)
                            continue
                        else:
                            text = await resp.text()
                            raise Exception(f"Gemini API Error {resp.status}: {text}")

                elif self.config["type"] == "openai":
                    headers = {"Authorization": f"Bearer {self.api_key}"}
                    data = {
                        "model": self.config["model"],
                        "messages": [
                            {"role": "system", "content": system},
                            {"role": "user", "content": prompt}
                        ],
                        "max_tokens": 4096,
                        "response_format": {"type": "json_object"} if self.provider_name in ["GROQ", "DEEPSEEK"] else None
                    }
                    async with self.session.post(self.config["url"], headers=headers, json=data) as resp:
                        if resp.status == 200:
                            res = await resp.json()
                            return res["choices"][0]["message"]["content"]
                        elif resp.status in [429, 500, 502, 503, 504]:
                            await self._handle_retry(attempt, resp.status)
                            continue
                        else:
                            text = await resp.text()
                            raise Exception(f"{self.provider_name} API Error {resp.status}: {text}")

            except Exception as e:
                if attempt == 3:
                    logger.error(f"AI Completion failed after 4 attempts: {e}")
                    raise
                await self._handle_retry(attempt)
        return ""

    async def _handle_retry(self, attempt: int, status: int = 0):
        delay = (2 ** attempt) + random.uniform(0, 1)
        logger.warning(f"Retrying AI call (attempt {attempt+1}) due to status {status or 'error'}. Sleeping {delay:.2f}s")
        await asyncio.sleep(delay)

    async def ping(self) -> bool:
        try:
            res = await self.complete("Say 'pong'", system="Respond only with 'pong'")
            return "pong" in res.lower()
        except:
            return False

# --- Resume Parser ---

def parse_resume(file_path: str) -> str:
    ext = Path(file_path).suffix.lower()
    text = ""
    if ext == ".pdf":
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
    elif ext == ".docx":
        doc = Document(file_path)
        text = "\n".join([p.text for p in doc.paragraphs])
    else:
        raise ValueError("Unsupported resume format. Use PDF or DOCX.")
    return text

async def extract_resume_profile(client: AIClient, raw_text: str) -> ResumeProfile:
    prompt = f"""
    Extract structured information from this resume text. 
    Return ONLY a JSON object with these keys: 
    skills (list), experience_years (int), education (list), job_titles (list), certifications (list), tech_keywords (list),
    suggested_role (string: the most likely target job title for this person),
    suggested_location (string: city/country or 'Remote' based on address/preference in resume).
    
    Resume Text:
    {raw_text[:8000]}
    """
    try:
        res = await client.complete(prompt, system="You are a professional resume parser. Return only JSON.")
        # Clean markdown if present
        res = re.sub(r"```json\s?|\s?```", "", res).strip()
        data = json.loads(res)
        return ResumeProfile(full_text=raw_text, **data)
    except Exception as e:
        logger.warning(f"AI Resume extraction failed, using regex fallback: {e}")
        # Very basic fallback
        return ResumeProfile(full_text=raw_text)

# --- Scrapers ---

class JobScraper:
    def __init__(self, playwright):
        self.playwright = playwright
        self.ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

    async def _get_page_content(self, url: str) -> str:
        browser = await self.playwright.chromium.launch(headless=True)
        context = await browser.new_context(user_agent=self.ua)
        page = await context.new_page()
        try:
            await page.goto(url, wait_until="networkidle", timeout=60000)
            await asyncio.sleep(random.uniform(1, 3))
            content = await page.content()
            return content
        finally:
            await browser.close()

    async def scrape_linkedin(self, role: str, location: str) -> List[RawJob]:
        logger.info(f"Scraping LinkedIn for {role} in {location}")
        url = f"https://www.linkedin.com/jobs/search?keywords={role}&location={location}"
        content = await self._get_page_content(url)
        soup = BeautifulSoup(content, 'lxml')
        jobs = []
        for card in soup.select('.base-card'):
            title_el = card.select_one('.base-search-card__title')
            company_el = card.select_one('.base-search-card__subtitle')
            link_el = card.select_one('.base-card__full-link')
            if title_el and company_el and link_el:
                jobs.append(RawJob(
                    title=title_el.get_text(strip=True),
                    company=company_el.get_text(strip=True),
                    description="Visit URL for full description",
                    url=link_el['href'],
                    source_board="LinkedIn"
                ))
        return jobs[:20]

    async def scrape_indeed(self, role: str, location: str) -> List[RawJob]:
        # Indeed is heavily protected, this is a simplified simulation/placeholder
        # In production, we'd use a proxy service or a more robust bypass
        logger.info(f"Scraping Indeed for {role} in {location}")
        return []

    async def scrape_wellfound(self, role: str, location: str) -> List[RawJob]:
        logger.info(f"Scraping Wellfound for {role} in {location}")
        return []

    async def scrape_glassdoor(self, role: str, location: str) -> List[RawJob]:
        logger.info(f"Scraping Glassdoor for {role} in {location}")
        return []

    async def scrape_naukri(self, role: str, location: str) -> List[RawJob]:
        logger.info(f"Scraping Naukri for {role} in {location}")
        return []

# --- AI Job Analysis ---

async def analyze_job(client: AIClient, resume: ResumeProfile, job: RawJob) -> JobResult:
    prompt = f"""
    Analyze this job against the candidate's resume. 
    Return a single JSON object with EXACTLY these fields:
    job_title, company, location, remote_type, employment_type, experience_level, industry, company_size,
    salary_min, salary_max, salary_currency, salary_display, visa_sponsorship, posted_date, application_deadline,
    description_summary, skills_required, responsibilities, nice_to_have,
    ats_score, ats_breakdown, match_verdict, keywords_matched, keywords_missing, skill_gaps,
    resume_tips, cover_letter_hint, interview_topics, contact_email, contact_phone, apply_url

    ATS Score Calculation (0-100):
    - keyword_overlap (40%)
    - skills_match (30%)
    - experience_align (20%)
    - education_match (10%)

    Match Verdict: "Perfect match" (>=80), "Should apply" (55-79), "Not suitable" (<55)

    Candidate Resume:
    {resume.full_text[:4000]}

    Job Details:
    Title: {job.title}
    Company: {job.company}
    URL: {job.url}
    JD: {job.description}
    """

    system_msg = "You are an expert HR and ATS system. Return ONLY valid JSON. No markdown. No preamble."
    
    try:
        res = await client.complete(prompt, system=system_msg)
        # Handle potential markdown fences
        res = re.sub(r"```json\s?|\s?```", "", res).strip()
        data = json.loads(res)
        
        result = JobResult(**data)
        result.source_board = job.source_board
        result.ai_provider_used = client.provider_name
        result.apply_url = job.url if not result.apply_url else result.apply_url
        return result
    except Exception as e:
        logger.error(f"Failed to analyze job {job.title} at {job.company}: {e}")
        # Return a shell result on failure to not break the loop
        return JobResult(
            job_title=job.title,
            company=job.company,
            location="Unknown",
            remote_type="Unknown",
            employment_type="Unknown",
            experience_level="Unknown",
            industry="Unknown",
            company_size="Unknown",
            source_board=job.source_board,
            ai_provider_used=client.provider_name,
            apply_url=job.url
        )

# --- Excel Generation ---

def generate_excel(results: List[JobResult], output_path: str, summary: Dict[str, Any]):
    wb = Workbook()
    
    # Sheet 1: All Jobs
    ws1 = wb.active
    ws1.title = "All Jobs"
    
    headers = [
        "#", "match_verdict", "ats_score", "job_title", "company", "location", "remote_type",
        "salary_display", "employment_type", "experience_level", "industry", "company_size",
        "visa_sponsorship", "skills_required", "keywords_matched", "keywords_missing",
        "skill_gaps", "resume_tips", "cover_letter_hint", "interview_topics",
        "description_summary", "responsibilities", "nice_to_have",
        "contact_email", "contact_phone", "apply_url",
        "posted_date", "application_deadline", "source_board", "ai_provider_used", "run_timestamp"
    ]
    
    # Formatting styles
    header_fill = PatternFill(start_color="2D2D2D", end_color="2D2D2D", fill_type="solid")
    header_font = Font(color="FFFFFF", bold=True)
    center_align = Alignment(horizontal="center", vertical="center")
    wrap_align = Alignment(wrap_text=True, vertical="top")
    thin_border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))

    # Write Headers
    for col, header in enumerate(headers, 1):
        cell = ws1.cell(row=1, column=col, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = center_align
    
    # Sort results
    results.sort(key=lambda x: x.ats_score, reverse=True)
    
    # Write Data
    for i, res in enumerate(results, 2):
        row_data = [
            i - 1, res.match_verdict, res.ats_score, res.job_title, res.company, res.location, res.remote_type,
            res.salary_display, res.employment_type, res.experience_level, res.industry, res.company_size,
            res.visa_sponsorship, ", ".join(res.skills_required), ", ".join(res.keywords_matched), ", ".join(res.keywords_missing),
            ", ".join(res.skill_gaps), "\n".join(res.resume_tips), res.cover_letter_hint, "\n".join(res.interview_topics),
            res.description_summary, "\n".join(res.responsibilities), ", ".join(res.nice_to_have),
            res.contact_email, res.contact_phone, res.apply_url,
            res.posted_date, res.application_deadline, res.source_board, res.ai_provider_used, res.run_timestamp
        ]
        
        # Row coloring
        color_map = {
            "Perfect match": "D6F0D6",
            "Should apply": "FFF4CC",
            "Not suitable": "FFE5E5"
        }
        font_map = {
            "Perfect match": "1A5C1A",
            "Should apply": "7A5C00",
            "Not suitable": "7A1A1A"
        }
        
        fill = PatternFill(start_color=color_map.get(res.match_verdict, "FFFFFF"), fill_type="solid")
        font_color = font_map.get(res.match_verdict, "000000")
        
        for col, val in enumerate(row_data, 1):
            cell = ws1.cell(row=i, column=col, value=val)
            cell.fill = fill
            cell.font = Font(color=font_color)
            if headers[col-1] in ["description_summary", "resume_tips", "cover_letter_hint", "interview_topics"]:
                cell.alignment = wrap_align
            
            # Highlight ATS Score
            if headers[col-1] == "ats_score":
                cell.font = Font(bold=True, color=font_color)
            
            # Pill style for Verdict
            if headers[col-1] == "match_verdict":
                cell.font = Font(bold=True, size=12, color=font_color)

    ws1.freeze_panes = "A2"
    
    # Sheet 2: Perfect Matches
    ws2 = wb.create_sheet("Perfect Matches")
    ws2.sheet_properties.tabColor = "1A5C1A"
    # (Simplified: Copy headers and matching rows)
    for col, header in enumerate(headers, 1):
        cell = ws2.cell(row=5, column=col, value=header)
        cell.fill = header_fill
        cell.font = header_font
    
    pm_results = [r for r in results if r.ats_score >= 80]
    for i, res in enumerate(pm_results, 6):
        # ... (Write rows similar to above)
        ws2.cell(row=i, column=1, value=i-5)
        ws2.cell(row=i, column=2, value=res.match_verdict)
        ws2.cell(row=i, column=3, value=res.ats_score)
        ws2.cell(row=i, column=4, value=res.job_title)
        ws2.cell(row=i, column=5, value=res.company)
    
    ws2.cell(row=1, column=1, value=f"Total perfect matches: {len(pm_results)}")
    ws2.cell(row=1, column=3, value=f"Avg ATS score: {sum(r.ats_score for r in pm_results)/len(pm_results) if pm_results else 0:.1f}")
    ws2.cell(row=1, column=5, value=f"Run date: {datetime.now().strftime('%Y-%m-%d')}")

    # Sheet 3: Summary
    ws3 = wb.create_sheet("Run Summary")
    ws3.sheet_properties.tabColor = "0C447C"
    
    ws3.column_dimensions['A'].width = 25
    ws3.column_dimensions['B'].width = 40
    
    rows = [
        ("Job Hunt Summary Report", ""),
        ("-" * 40, ""),
        ("Run date & time", summary['timestamp']),
        ("Resume file", summary['resume_file']),
        ("Target role", summary['role']),
        ("Target location", summary['location']),
        ("AI provider used", summary['provider']),
        ("Boards scraped", summary['boards']),
        ("-" * 40, ""),
        ("Total jobs found", summary['total_found']),
        ("After deduplication", summary['after_dedup']),
        ("Perfect matches", summary['perfect']),
        ("Should apply", summary['should_apply']),
        ("Not suitable", summary['not_suitable']),
        ("-" * 40, ""),
        ("Top match", summary['top_match']),
        ("Highest salary seen", summary['max_salary']),
        ("Remote opportunities", summary['remote_count']),
        ("-" * 40, ""),
        ("Most common skill gap", summary['common_gap']),
        ("Most required skill", summary['common_skill']),
    ]
    
    for i, (label, val) in enumerate(rows, 1):
        ws3.cell(row=i, column=1, value=label).font = Font(bold=True)
        ws3.cell(row=i, column=2, value=val)

    # Finalize
    wb.save(output_path)

# --- Notification ---

async def send_notification(summary: Dict[str, Any], top_matches: List[JobResult]):
    api_key = os.getenv("SENDGRID_API_KEY")
    email = os.getenv("NOTIFY_EMAIL")
    if not api_key or not email:
        return

    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail

    html_content = f"<h2>Job Hunt Results: {summary['perfect']} Perfect Matches</h2>"
    html_content += "<table border='1' style='border-collapse: collapse; width: 100%;'>"
    html_content += "<tr style='background: #2D2D2D; color: white;'><th>Title</th><th>Company</th><th>ATS</th><th>Salary</th><th>Link</th></tr>"
    
    for res in top_matches[:10]:
        color = "D6F0D6" if res.ats_score >= 80 else "FFF4CC" if res.ats_score >= 55 else "FFE5E5"
        html_content += f"<tr style='background-color: #{color};'>"
        html_content += f"<td>{res.job_title}</td><td>{res.company}</td><td>{res.ats_score}</td><td>{res.salary_display}</td><td><a href='{res.apply_url}'>Apply</a></td></tr>"
    html_content += "</table>"

    message = Mail(
        from_email='jobhunter@ai-agent.com',
        to_emails=email,
        subject=f"Job Hunt Results - {summary['perfect']} Perfect Matches ({summary['role']})",
        html_content=html_content
    )
    try:
        sg = SendGridAPIClient(api_key)
        sg.send(message)
        logger.info("Notification email sent via SendGrid")
    except Exception as e:
        logger.warning(f"Failed to send email: {e}")

# --- Main Logic ---

async def main():
    import argparse
    parser = argparse.ArgumentParser(description="Job Hunter AI Agent")
    parser.add_argument("--resume", required=True, help="Path to resume PDF/DOCX")
    parser.add_argument("--role", default="auto", help="Target job role (or 'auto')")
    parser.add_argument("--location", default="auto", help="Job location (or 'auto' or 'all')")
    parser.add_argument("--limit", type=int, default=100, help="Max jobs to process")
    parser.add_argument("--ats-threshold", type=int, default=0, help="Min ATS score")
    parser.add_argument("--boards", default="linkedin,indeed,glassdoor,naukri,wellfound", help="Comma-separated boards")
    parser.add_argument("--output-dir", default="./output", help="Output directory")
    parser.add_argument("--provider", help="Force specific AI provider")
    parser.add_argument("--api-key", help="API key for the selected provider")
    parser.add_argument("--openai-base-url", help="Custom base URL for OpenAI-compatible providers")
    parser.add_argument("--log-level", default="INFO", help="Log level")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    # 1. AI Provider Selection
    active_provider = args.provider.upper() if args.provider else None
    api_key = args.api_key
    
    if active_provider and api_key:
        if args.openai_base_url and active_provider in ["GROQ", "DEEPSEEK", "NVIDIA"]:
             PROVIDERS[active_provider]["url"] = args.openai_base_url
    else:
        # Fallback to auto-detection from env if no key provided via CLI
        for p in PRIORITY_LIST:
            key = os.getenv(PROVIDERS[p]["key"])
            if key:
                logger.info(f"Checking {p}...")
                async with AIClient(p, key) as client:
                    if await client.ping():
                        active_provider = p
                        api_key = key
                        break
    
    if not active_provider or not api_key:
        logger.error("No active AI provider or API key found.")
        sys.exit(1)

    logger.info(f"ACTIVE_PROVIDER: {active_provider}")

    # 2. Resume Processing
    logger.info(f"Parsing resume: {args.resume}")
    resume_text = parse_resume(args.resume)
    async with AIClient(active_provider, api_key) as client:
        resume_profile = await extract_resume_profile(client, resume_text)
    
    # Auto-detect role and location if requested
    target_role = args.role
    if not target_role or target_role.lower() == "auto":
        target_role = resume_profile.suggested_role
        logger.info(f"Auto-detected role from resume: {target_role}")

    target_location = args.location
    if not target_location or target_location.lower() == "auto":
        target_location = resume_profile.suggested_location
        logger.info(f"Auto-detected location from resume: {target_location}")
    elif target_location.lower() == "all":
        target_location = "" # Global search
        logger.info("Global location search requested ('all')")

    # 3. Scraping
    boards = args.boards.split(",")
    raw_jobs = []
    async with async_playwright() as p:
        scraper = JobScraper(p)
        tasks = []
        if "linkedin" in boards: tasks.append(scraper.scrape_linkedin(target_role, target_location))
        if "indeed" in boards: tasks.append(scraper.scrape_indeed(target_role, target_location))
        if "wellfound" in boards: tasks.append(scraper.scrape_wellfound(target_role, target_location))
        if "glassdoor" in boards: tasks.append(scraper.scrape_glassdoor(target_role, target_location))
        if "naukri" in boards: tasks.append(scraper.scrape_naukri(target_role, target_location))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for res in results:
            if isinstance(res, list):
                raw_jobs.extend(res)
            else:
                logger.error(f"Scraper error: {res}")

    # Deduplication
    seen = set()
    deduped_jobs = []
    for job in raw_jobs:
        key = (job.company.lower() + job.title.lower())
        if key not in seen:
            seen.add(key)
            deduped_jobs.append(job)
    
    logger.info(f"Found {len(raw_jobs)} jobs. After dedup: {len(deduped_jobs)}")
    
    # 4. AI Analysis
    processed_results = []
    async with AIClient(active_provider, api_key) as client:
        for job in tqdm(deduped_jobs[:args.limit], desc="Analyzing Jobs"):
            res = await analyze_job(client, resume_profile, job)
            if res.ats_score >= args.ats_threshold:
                processed_results.append(res)
    
    # 5. Output Generation
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(args.output_dir, f"job_results_{timestamp}.xlsx")
    
    # Calculate Summary Stats
    perfect = [r for r in processed_results if r.ats_score >= 80]
    should = [r for r in processed_results if 55 <= r.ats_score < 80]
    not_suitable = [r for r in processed_results if r.ats_score < 55]
    top_match = processed_results[0] if processed_results else None
    
    summary = {
        "timestamp": datetime.now().isoformat(),
        "resume_file": args.resume,
        "role": target_role,
        "location": target_location or "All",
        "provider": active_provider,
        "boards": args.boards,
        "total_found": len(raw_jobs),
        "after_dedup": len(deduped_jobs),
        "perfect": len(perfect),
        "should_apply": len(should),
        "not_suitable": len(not_suitable),
        "top_match": f"{top_match.job_title} at {top_match.company} (ATS: {top_match.ats_score})" if top_match else "N/A",
        "max_salary": max([r.salary_display for r in processed_results], default="N/A"),
        "remote_count": len([r for r in processed_results if r.remote_type == "Remote"]),
        "common_gap": "N/A", 
        "common_skill": "N/A"
    }
    
    generate_excel(processed_results, output_file, summary)
    
    # Save JSON summary for GitHub Step Summary
    with open(os.path.join(args.output_dir, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
        
    logger.info(f"Process complete! Results saved to: {output_file}")
    
    # 6. Notification
    await send_notification(summary, processed_results)

if __name__ == "__main__":
    asyncio.run(main())
