#!/usr/bin/env python3
"""
Job Hunter - Streamlit UI
Local web interface for running the Job Hunter agent
"""

import streamlit as st
import asyncio
import os
import sys
import json
from pathlib import Path
from datetime import datetime
from io import BytesIO
import logging

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from job_hunter import (
    setup_logging,
    detect_active_provider,
    parse_resume_file,
    extract_resume_profile,
    scrape_all_jobs,
    analyze_job,
    create_excel_output,
    ResumeProfile,
    JobResult,
)

from dotenv import load_dotenv

# ============================================================================
# STREAMLIT CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Job Hunter 🎯",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Add custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 1rem;
    }
    .stats-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    .stats-value {
        font-size: 2rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    .stats-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    .perfect-match {
        background-color: #d6f0d6;
        color: #1a5c1a;
    }
    .should-apply {
        background-color: #fff4cc;
        color: #7a5c00;
    }
    .not-suitable {
        background-color: #ffe5e5;
        color: #7a1a1a;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# INITIALIZE SESSION STATE
# ============================================================================

if "jobs" not in st.session_state:
    st.session_state.jobs = []
if "resume" not in st.session_state:
    st.session_state.resume = None
if "provider_name" not in st.session_state:
    st.session_state.provider_name = None
if "running" not in st.session_state:
    st.session_state.running = False
if "resume_profile" not in st.session_state:
    st.session_state.resume_profile = None
if "summary_stats" not in st.session_state:
    st.session_state.summary_stats = None

# ============================================================================
# LOGGING
# ============================================================================

logger = logging.getLogger(__name__)

# ============================================================================
# UI SECTIONS
# ============================================================================

def render_header():
    """Render the header section"""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown('<div class="main-header">🎯 Job Hunter</div>', unsafe_allow_html=True)
        st.markdown("*AI-powered job hunting agent — find your perfect role in minutes*")
    with col2:
        st.info(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")

def render_sidebar():
    """Render the sidebar with configuration options"""
    st.sidebar.title("⚙️ Configuration")
    
    # Resume upload
    st.sidebar.markdown("### 📄 Resume")
    resume_file = st.sidebar.file_uploader(
        "Upload your resume (PDF or DOCX)",
        type=["pdf", "docx"],
        help="Your resume will be parsed to extract skills, experience, and qualifications"
    )
    
    if resume_file:
        st.session_state.resume = resume_file
        st.sidebar.success("✓ Resume uploaded")
    
    # Search parameters
    st.sidebar.markdown("### 🔍 Search Parameters")
    
    search_role = st.sidebar.text_input(
        "Target job role",
        value="Software Engineer",
        placeholder="e.g., Backend Engineer, Data Scientist",
        help="The job title you're looking for"
    )
    
    search_location = st.sidebar.text_input(
        "Target location",
        value="Remote",
        placeholder="e.g., Remote, San Francisco, Bangalore",
        help="Job location or 'Remote' for remote jobs"
    )
    
    job_limit = st.sidebar.slider(
        "Max jobs to analyze",
        min_value=10,
        max_value=500,
        value=100,
        step=10,
        help="Higher limit = more comprehensive but slower"
    )
    
    # Board selection
    st.sidebar.markdown("### 🏢 Job Boards")
    boards = st.sidebar.multiselect(
        "Select job boards to scrape",
        ["linkedin", "indeed", "glassdoor", "naukri", "wellfound"],
        default=["linkedin", "indeed", "glassdoor"],
        help="Which job boards to search"
    )
    
    # Filters
    st.sidebar.markdown("### 🎯 Filters")
    ats_threshold = st.sidebar.slider(
        "Minimum ATS score",
        min_value=0,
        max_value=100,
        value=0,
        step=5,
        help="Only show jobs with ATS score >= this value"
    )
    
    # AI Provider
    st.sidebar.markdown("### 🤖 AI Provider")
    load_dotenv()
    available_providers = []
    if os.getenv("ANTHROPIC_API_KEY"):
        available_providers.append("claude")
    if os.getenv("GEMINI_API_KEY"):
        available_providers.append("gemini")
    if os.getenv("GROQ_API_KEY"):
        available_providers.append("groq")
    if os.getenv("DEEPSEEK_API_KEY"):
        available_providers.append("deepseek")
    if os.getenv("NVIDIA_API_KEY"):
        available_providers.append("nvidia")
    
    if not available_providers:
        st.sidebar.error("❌ No AI provider keys found in .env")
    else:
        forced_provider = st.sidebar.selectbox(
            "AI Provider",
            ["Auto-detect"] + available_providers,
            help="Leave as 'Auto-detect' to use the first available provider"
        )
    
    return {
        "resume_file": resume_file,
        "search_role": search_role,
        "search_location": search_location,
        "job_limit": job_limit,
        "boards": boards,
        "ats_threshold": ats_threshold,
        "forced_provider": None if forced_provider == "Auto-detect" else forced_provider,
        "available_providers": available_providers
    }

def render_main_content(config):
    """Render the main content area"""
    if not config["resume_file"]:
        st.warning("👈 Please upload your resume in the sidebar to get started")
        return
    
    if not config["boards"]:
        st.warning("👈 Please select at least one job board in the sidebar")
        return
    
    # Main tabs
    tab1, tab2, tab3 = st.tabs(["🔍 Run Search", "📊 Results", "📈 Analytics"])
    
    with tab1:
        render_search_tab(config)
    
    with tab2:
        render_results_tab(config)
    
    with tab3:
        render_analytics_tab()

def render_search_tab(config):
    """Render the search/run tab"""
    st.markdown("### 🚀 Job Hunt Execution")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Target Role", config["search_role"])
    with col2:
        st.metric("Location", config["search_location"])
    with col3:
        st.metric("Max Jobs", config["job_limit"])
    
    st.markdown("---")
    
    # Run button
    if st.button("🔍 Start Job Hunt", key="run_button", use_container_width=True):
        st.session_state.running = True
        asyncio.run(run_job_hunt(config))
    
    # Show progress
    if st.session_state.running or st.session_state.jobs:
        st.markdown("### 📋 Progress")
        
        if st.session_state.jobs:
            col1, col2, col3, col4 = st.columns(4)
            
            total_jobs = len(st.session_state.jobs)
            perfect = len([j for j in st.session_state.jobs if j.ats_score >= 80])
            should_apply = len([j for j in st.session_state.jobs if 55 <= j.ats_score < 80])
            not_suitable = len([j for j in st.session_state.jobs if j.ats_score < 55])
            
            with col1:
                st.metric("Total Jobs Analyzed", total_jobs)
            with col2:
                st.metric("Perfect Matches", perfect, delta="✓")
            with col3:
                st.metric("Should Apply", should_apply)
            with col4:
                st.metric("Not Suitable", not_suitable)
            
            st.success(f"✓ Job hunt complete! {total_jobs} jobs analyzed.")

def render_results_tab(config):
    """Render the results tab"""
    if not st.session_state.jobs:
        st.info("📊 Run a job hunt search to see results here")
        return
    
    st.markdown("### 📊 Job Results")
    
    jobs = st.session_state.jobs
    
    # Filter by ATS threshold
    filtered_jobs = [j for j in jobs if j.ats_score >= config["ats_threshold"]]
    
    if not filtered_jobs:
        st.warning(f"No jobs meet the ATS threshold of {config['ats_threshold']}")
        return
    
    st.markdown(f"Showing {len(filtered_jobs)} of {len(jobs)} jobs")
    
    # Sort dropdown
    sort_by = st.selectbox(
        "Sort by",
        ["ATS Score (Highest)", "ATS Score (Lowest)", "Salary (Highest)", "Company Name"],
        key="sort_select"
    )
    
    if sort_by == "ATS Score (Highest)":
        filtered_jobs = sorted(filtered_jobs, key=lambda x: x.ats_score, reverse=True)
    elif sort_by == "ATS Score (Lowest)":
        filtered_jobs = sorted(filtered_jobs, key=lambda x: x.ats_score)
    elif sort_by == "Salary (Highest)":
        filtered_jobs = sorted(filtered_jobs, key=lambda x: x.salary_max or 0, reverse=True)
    elif sort_by == "Company Name":
        filtered_jobs = sorted(filtered_jobs, key=lambda x: x.company)
    
    # Filter by verdict
    verdict_filter = st.multiselect(
        "Filter by match verdict",
        ["Perfect match", "Should apply", "Not suitable"],
        default=["Perfect match", "Should apply", "Not suitable"],
        key="verdict_filter"
    )
    
    filtered_jobs = [j for j in filtered_jobs if j.match_verdict in verdict_filter]
    
    # Display jobs
    for idx, job in enumerate(filtered_jobs, 1):
        with st.container(border=True):
            # Color based on verdict
            verdict_color = {
                "Perfect match": "🟢",
                "Should apply": "🟡",
                "Not suitable": "🔴"
            }.get(job.match_verdict, "⚪")
            
            col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
            
            with col1:
                st.markdown(f"### {job.job_title}")
                st.markdown(f"**{job.company}** • {job.location}")
            
            with col2:
                st.markdown(f"**{verdict_color} {job.match_verdict}**")
                st.markdown(f"**ATS: {job.ats_score}/100**")
            
            with col3:
                if job.salary_display and job.salary_display != "Not disclosed":
                    st.markdown(f"💰 {job.salary_display}")
                if job.remote_type:
                    st.markdown(f"🏠 {job.remote_type}")
            
            with col4:
                if job.apply_url:
                    st.link_button("Apply", job.apply_url, use_container_width=True)
            
            # Expandable details
            with st.expander("📋 Details", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Job Info**")
                    st.write(f"• **Type:** {job.employment_type}")
                    st.write(f"• **Level:** {job.experience_level}")
                    st.write(f"• **Industry:** {job.industry}")
                    st.write(f"• **Size:** {job.company_size}")
                    st.write(f"• **Visa:** {job.visa_sponsorship}")
                
                with col2:
                    st.markdown("**ATS Breakdown**")
                    if job.ats_breakdown:
                        for metric, score in job.ats_breakdown.items():
                            st.write(f"• **{metric}:** {score}/100")
                
                st.markdown("**Summary**")
                st.write(job.description_summary)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Skills Required**")
                    st.write(", ".join(job.skills_required[:5]))
                    
                    st.markdown("**Matched Keywords**")
                    if job.keywords_matched:
                        st.write(", ".join(job.keywords_matched[:5]))
                
                with col2:
                    st.markdown("**Skill Gaps**")
                    if job.skill_gaps:
                        st.write(", ".join(job.skill_gaps[:5]))
                    
                    st.markdown("**Missing Keywords**")
                    if job.keywords_missing:
                        st.write(", ".join(job.keywords_missing[:5]))
                
                st.markdown("**Resume Tips**")
                for tip in job.resume_tips[:3]:
                    st.write(f"• {tip}")
                
                st.markdown("**Cover Letter Hints**")
                st.write(job.cover_letter_hint)
                
                st.markdown("**Interview Topics**")
                for topic in job.interview_topics[:3]:
                    st.write(f"• {topic}")
                
                if job.contact_email:
                    st.write(f"📧 Contact: {job.contact_email}")
    
    # Download Excel
    if st.session_state.summary_stats:
        st.markdown("---")
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("📥 Download Excel", use_container_width=True):
                st.info("Excel file was generated during the job hunt. Check the output folder.")

def render_analytics_tab():
    """Render the analytics tab"""
    if not st.session_state.jobs or not st.session_state.summary_stats:
        st.info("📈 Run a job hunt search to see analytics here")
        return
    
    st.markdown("### 📈 Job Hunt Analytics")
    
    jobs = st.session_state.jobs
    stats = st.session_state.summary_stats
    
    # Top metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="stats-card"><div class="stats-label">Perfect Matches</div><div class="stats-value">' + 
                   str(stats["perfect_matches"]) + '</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="stats-card"><div class="stats-label">Should Apply</div><div class="stats-value">' + 
                   str(stats["should_apply"]) + '</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="stats-card"><div class="stats-label">Remote Jobs</div><div class="stats-value">' + 
                   str(stats["remote_opportunities"]) + '</div></div>', unsafe_allow_html=True)
    with col4:
        avg_score = sum(j.ats_score for j in jobs) / len(jobs) if jobs else 0
        st.markdown('<div class="stats-card"><div class="stats-label">Avg ATS Score</div><div class="stats-value">' + 
                   f'{avg_score:.0f}</div></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # ATS Score Distribution
        st.markdown("### ATS Score Distribution")
        import matplotlib.pyplot as plt
        
        fig, ax = plt.subplots()
        ats_scores = [j.ats_score for j in jobs]
        ax.hist(ats_scores, bins=10, edgecolor='black', color='#667eea', alpha=0.7)
        ax.set_xlabel('ATS Score')
        ax.set_ylabel('Number of Jobs')
        ax.axvline(x=80, color='green', linestyle='--', label='Perfect (80+)')
        ax.axvline(x=55, color='orange', linestyle='--', label='Good (55+)')
        ax.legend()
        st.pyplot(fig)
    
    with col2:
        # Match Verdict Breakdown
        st.markdown("### Match Verdict Breakdown")
        
        verdicts = {}
        for job in jobs:
            verdicts[job.match_verdict] = verdicts.get(job.match_verdict, 0) + 1
        
        fig, ax = plt.subplots()
        colors = {
            "Perfect match": "#D6F0D6",
            "Should apply": "#FFF4CC",
            "Not suitable": "#FFE5E5"
        }
        ax.pie(verdicts.values(), labels=verdicts.keys(), autopct='%1.1f%%',
               colors=[colors.get(k, '#ccc') for k in verdicts.keys()])
        st.pyplot(fig)
    
    st.markdown("---")
    
    # Top insights
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Key Statistics")
        st.write(f"**Total Jobs Analyzed:** {len(jobs)}")
        st.write(f"**Average ATS Score:** {sum(j.ats_score for j in jobs) / len(jobs):.1f}")
        
        if jobs:
            top_job = max(jobs, key=lambda x: x.ats_score)
            st.write(f"**Top Match:** {top_job.job_title} at {top_job.company} (ATS: {top_job.ats_score})")
        
        salaries = [j.salary_max for j in jobs if j.salary_max]
        if salaries:
            st.write(f"**Highest Salary:** {max(salaries)} {jobs[0].salary_currency or 'USD'}")
    
    with col2:
        st.markdown("### 🎯 Skill Analysis")
        
        # Most required skills
        from collections import Counter
        all_skills = []
        for job in jobs:
            all_skills.extend(job.skills_required)
        
        if all_skills:
            skill_counter = Counter(all_skills)
            st.write("**Top 5 Required Skills:**")
            for skill, count in skill_counter.most_common(5):
                st.write(f"• {skill} ({count} jobs)")
        
        # Most common skill gaps
        all_gaps = []
        for job in jobs:
            all_gaps.extend(job.skill_gaps)
        
        if all_gaps:
            gap_counter = Counter(all_gaps)
            st.write("**Top 5 Skill Gaps:**")
            for gap, count in gap_counter.most_common(5):
                st.write(f"• {gap} ({count} jobs)")

async def run_job_hunt(config):
    """Run the job hunt asynchronously"""
    load_dotenv()
    
    # Create progress containers
    progress_container = st.container()
    status_container = st.container()
    
    with progress_container:
        st.markdown("### 🔄 Job Hunt in Progress...")
        progress_bar = st.progress(0)
        status_text = st.empty()
    
    try:
        # Resume handling
        resume_file = config["resume_file"]
        resume_path = Path(f"temp_{resume_file.name}")
        resume_path.write_bytes(resume_file.getbuffer())
        
        status_text.write("📄 Parsing resume...")
        resume_text = parse_resume_file(str(resume_path))
        progress_bar.progress(10)
        
        # Detect provider
        status_text.write("🤖 Detecting AI provider...")
        ai_client, provider_name = await detect_active_provider(config["forced_provider"])
        st.session_state.provider_name = provider_name
        progress_bar.progress(15)
        
        # Extract resume profile
        status_text.write("🧠 Extracting resume profile...")
        async with ai_client:
            resume_profile = await extract_resume_profile(resume_text, ai_client)
            st.session_state.resume_profile = resume_profile
            progress_bar.progress(25)
            
            # Scrape jobs
            status_text.write(f"🔍 Scraping jobs from {len(config['boards'])} boards...")
            raw_jobs = await scrape_all_jobs(
                config["search_role"],
                config["search_location"],
                config["boards"],
                config["job_limit"]
            )
            progress_bar.progress(50)
            
            if not raw_jobs:
                status_container.error("❌ No jobs found. Try different search parameters.")
                return
            
            # Analyze jobs
            status_text.write(f"🎯 Analyzing {len(raw_jobs)} jobs with AI...")
            analyzed_jobs = []
            
            for idx, raw_job in enumerate(raw_jobs):
                result = await analyze_job(raw_job, resume_profile, ai_client, provider_name)
                if result:
                    analyzed_jobs.append(result)
                
                progress = int(50 + (idx / len(raw_jobs)) * 40)
                progress_bar.progress(progress)
            
            progress_bar.progress(90)
            
            # Filter and store results
            if config["ats_threshold"] > 0:
                analyzed_jobs = [j for j in analyzed_jobs if j.ats_score >= config["ats_threshold"]]
            
            st.session_state.jobs = analyzed_jobs
            
            # Generate Excel
            status_text.write("📊 Generating Excel output...")
            xlsx_file, summary_data = create_excel_output(
                analyzed_jobs,
                "output",
                str(resume_path),
                config["search_role"],
                config["search_location"],
                provider_name
            )
            st.session_state.summary_stats = summary_data
            
            progress_bar.progress(100)
            status_text.write("✓ Job hunt complete!")
        
        # Cleanup
        if resume_path.exists():
            resume_path.unlink()
        
        st.session_state.running = False
        st.rerun()
    
    except Exception as e:
        status_container.error(f"❌ Error: {str(e)}")
        st.session_state.running = False

# ============================================================================
# MAIN APP
# ============================================================================

def main():
    """Main app"""
    render_header()
    
    config = render_sidebar()
    render_main_content(config)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #888; font-size: 0.9rem;">
    Made with ❤️ by Job Hunter | 
    <a href="https://github.com" target="_blank">GitHub</a> | 
    <a href="https://discord.gg" target="_blank">Discord</a>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
