import os
import sqlite3
import pandas as pd
import streamlit as st

from resume_parser import parse_resume
from job_search import search_jobs
from email_notifier import send_email_alert
from db_manager import init_db, store_candidate_profile, get_candidate_profile, update_job_status, get_job_statuses
from semantic_matcher import calculate_semantic_fit

# --- Job Roles Dataset ---
MASTER_JOB_ROLES = [
    "Python Developer", "Python Backend Developer", "Python Full Stack Developer",
    "Python Django / FastAPI Developer", "Python Data Engineer", "Python Machine Learning Engineer",
    "Java Developer", "Java Full Stack Developer", "Spring Boot Engineer",
    "React.js Developer", "Frontend Developer", "Full Stack Web Developer", "Node.js Developer",
    "Data Analyst", "Data Scientist", "DevOps Engineer", "Cloud Engineer (AWS/Azure)",
    "QA Automation Engineer", "Selenium Tester", "AI / Prompt Engineer"
]

# --- Page Config ---
st.set_page_config(page_title="SmartJobApply | Your AI Job Search Co-Pilot", page_icon="🚀", layout="wide")
init_db()

# --- Custom Styling for Modern Light-Gradient UI ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
    color: #1e293b;
}

/* Background Gradient like reference image */
.stApp {
    background: radial-gradient(circle at 10% 20%, rgba(224, 231, 255, 0.6) 0%, rgba(243, 232, 255, 0.7) 40%, rgba(255, 255, 255, 0.9) 100%);
}

/* Top Navbar */
.nav-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 20px;
    background: rgba(255, 255, 255, 0.85);
    backdrop-filter: blur(10px);
    border-radius: 16px;
    margin-bottom: 25px;
    border: 1px solid rgba(226, 232, 240, 0.8);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
}
.brand-logo {
    font-size: 1.4rem;
    font-weight: 800;
    color: #4f46e5;
    letter-spacing: -0.5px;
}

/* Hero Section */
.hero-badge {
    display: inline-block;
    background: #ede9fe;
    color: #6366f1;
    font-size: 0.85rem;
    font-weight: 600;
    padding: 6px 18px;
    border-radius: 50px;
    margin-bottom: 12px;
}
.hero-title {
    font-size: 2.8rem;
    font-weight: 800;
    color: #334155;
    line-height: 1.2;
    margin-bottom: 8px;
}
.hero-subtitle {
    font-size: 1.4rem;
    font-weight: 700;
    color: #d97706;
    margin-bottom: 25px;
}

/* Feature Badges */
.feature-pill-row {
    display: flex;
    justify-content: center;
    gap: 12px;
    flex-wrap: wrap;
    margin-bottom: 30px;
}
.pill {
    padding: 8px 16px;
    border-radius: 50px;
    font-size: 0.88rem;
    font-weight: 600;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #ffffff;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.pill-red { border: 1px solid #fecaca; color: #dc2626; }
.pill-blue { border: 1px solid #bfdbfe; color: #2563eb; }
.pill-green { border: 1px solid #bbf7d0; color: #16a34a; }
.pill-purple { border: 1px solid #ddd6fe; color: #7c3aed; }
.pill-amber { border: 1px solid #fde68a; color: #d97706; }

/* Stat Box */
.stats-card {
    background: #ffffff;
    border-radius: 20px;
    padding: 30px 20px;
    margin: 25px auto;
    max-width: 800px;
    box-shadow: 0 10px 30px rgba(99, 102, 241, 0.08);
    border: 1px solid #e2e8f0;
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    text-align: center;
}
.stat-num {
    font-size: 1.8rem;
    font-weight: 800;
    color: #6366f1;
}
.stat-lbl {
    font-size: 0.8rem;
    color: #64748b;
    font-weight: 600;
}

/* Job Card */
.job-card {
    background: #ffffff;
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 15px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 4px 12px rgba(0,0,0,0.03);
}

.tag-match { background: #dcfce7; color: #15803d; padding: 3px 8px; border-radius: 6px; font-size: 0.78rem; font-weight: 600; margin-right: 4px; }
.tag-gap { background: #fee2e2; color: #b91c1c; padding: 3px 8px; border-radius: 6px; font-size: 0.78rem; font-weight: 600; margin-right: 4px; }

/* Footer */
.footer-box {
    margin-top: 60px;
    padding: 25px;
    text-align: center;
    border-top: 1px solid #e2e8f0;
    color: #64748b;
    font-size: 0.95rem;
}
</style>
""", unsafe_allow_html=True)

# --- Top Navbar ---
st.markdown("""
<div class='nav-container'>
    <div class='brand-logo'>SmartJobApply</div>
    <div style='display:flex; gap: 20px; font-weight:600; color:#475569; font-size:0.9rem;'>
        <span>Home</span>
        <span>Search Jobs</span>
        <span>Features</span>
        <span>Saved Jobs</span>
        <span>Auto-Apply</span>
    </div>
    <div>
        <span style='background:#4f46e5; color:white; padding:8px 18px; border-radius:8px; font-size:0.85rem; font-weight:700;'>Get Started</span>
    </div>
</div>
""", unsafe_allow_html=True)

# --- Hero Header Section ---
st.markdown("""
<div style='text-align: center; margin-top: 10px;'>
    <div class='hero-badge'>⭐ AI-Powered Job Matching</div>
    <div class='hero-title'>Your AI Job Search Co-Pilot</div>
    <div class='hero-subtitle'>Faster Applications. Smarter Matches. Better Opportunities.</div>
    <div class='feature-pill-row'>
        <div class='pill pill-red'>🎯 AI Match Score</div>
        <div class='pill pill-blue'>📄 Auto-Fill in 2 Secs</div>
        <div class='pill pill-green'>⚡ Instant Auto-Apply</div>
        <div class='pill pill-purple'>⭐ AI-Generated Messages</div>
        <div class='pill pill-amber'>🔔 Smart Job Alerts</div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- 4 Metrics Stats Banner ---
st.markdown("""
<div class='stats-card'>
    <div>
        <div class='stat-num'>10,000+</div>
        <div class='stat-lbl'>Applications Filled</div>
    </div>
    <div>
        <div class='stat-num'>5x</div>
        <div class='stat-lbl'>Faster Job Search</div>
    </div>
    <div>
        <div class='stat-num'>10+</div>
        <div class='stat-lbl'>Job Boards Unified</div>
    </div>
    <div>
        <div class='stat-num'>10 hrs</div>
        <div class='stat-lbl'>Saved Per Week</div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- Sidebar Resume Candidate Upload ---
with st.sidebar:
    st.markdown("### 📄 Resume Ingestion")
    uploaded_file = st.file_uploader("Upload PDF Resume", type=["pdf"])
    if uploaded_file and st.button("Generate Candidate Embeddings", use_container_width=True):
        temp_path = f"temp_{uploaded_file.name}"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        try:
            store_candidate_profile(parse_resume(temp_path))
            st.success("Candidate Profile Initialized!")
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
    profile = get_candidate_profile()
    if profile:
        skills = profile.get("skills", [])
        st.markdown(f"**Candidate:** `{profile.get('full_name')}`\n\n**Email:** `{profile.get('email')}`")
        st.markdown("".join([f"<span class='tag-match'>{s}</span>" for s in skills]), unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align: center; color: #64748b; font-size: 0.85rem;'>
        <b>System Architect</b><br>
        <span style='color: #4f46e5; font-weight: bold;'>Dongavath Pradeep</span><br><br>
        <a href='https://github.com/DongavathPradeep' target='_blank' style='color:#4f46e5; text-decoration:none;'>🔗 GitHub</a> | 
        <a href='https://www.linkedin.com/in/pradeep-naik-42292b264/' target='_blank' style='color:#4f46e5; text-decoration:none;'>💼 LinkedIn</a>
    </div>
    """, unsafe_allow_html=True)

# --- Interactive Search Section ---
st.markdown("<h3 style='text-align:center; color:#334155; margin-top:30px;'>🔍 Discover Your AI Matched Opportunities</h3>", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns([2.2, 1.1, 1.1, 0.9])
role_query = col1.text_input("Target Role", value="Python")
exp_level = col2.selectbox("Experience", ["Fresher", "1-3 yrs", "4+ yrs", "All"])
location_query = col3.selectbox("Location", ["Hyderabad", "Bangalore", "Pune", "Chennai", "Remote"])

# Live Keyword Role Suggestion Tags
if role_query.strip():
    matching_roles = [r for r in MASTER_JOB_ROLES if role_query.strip().lower() in r.lower()]
    if matching_roles:
        tags_html = "".join([f"<span style='background:#f1f5f9; color:#475569; padding:3px 8px; margin:2px; border-radius:4px; font-size:0.75rem; display:inline-block;'>{r}</span>" for r in matching_roles])
        st.markdown(f"<div style='margin-top:-10px; margin-bottom:12px;'><small style='color:#64748b;'><b>Related Roles:</b></small> {tags_html}</div>", unsafe_allow_html=True)

if "jobs_data" not in st.session_state:
    st.session_state["jobs_data"] = []

if col4.button("Search & Match", use_container_width=True) and profile:
    with st.spinner("Analyzing semantic fit across live job market..."):
        raw = search_jobs(role=role_query, location=location_query)
        st.session_state["jobs_data"] = calculate_semantic_fit(profile, raw)

# Display Search Results
results = st.session_state.get("jobs_data", [])
statuses = get_job_statuses()

if results:
    for idx, job in enumerate(results):
        matched_html = "".join([f"<span class='tag-match'>✓ {s}</span>" for s in job.get("matched_skills", [])]) or "None"
        missing_html = "".join([f"<span class='tag-gap'>✗ {s}</span>" for s in job.get("missing_skills", [])]) or "<span style='color:#16a34a;'>None</span>"
        
        st.markdown(f"""
        <div class='job-card'>
            <div style='display:flex; justify-content:space-between; align-items:center;'>
                <h4 style='color:#1e293b; margin:0;'>{job.get('title')}</h4>
                <span style='background:#dcfce7; color:#15803d; font-weight:800; padding:4px 12px; border-radius:50px; font-size:0.85rem;'>{job.get('semantic_score')}% Match</span>
            </div>
            <p style='color:#64748b; font-size:0.9rem; margin: 4px 0 10px 0;'><b>{job.get('company')}</b> • {job.get('location')}</p>
            <div style='margin-bottom:6px; font-size:0.85rem;'><b>Matches:</b> {matched_html}</div>
            <div style='font-size:0.85rem;'><b>Skill Gaps:</b> {missing_html}</div>
        </div>
        """, unsafe_allow_html=True)
        
        c1, c2 = st.columns([3, 1])
        if job.get("url"):
            c1.markdown(f"[🚀 **Instant Apply via Portal**]({job.get('url')})")
        
        current_status = statuses.get(f"{job.get('title')}--{job.get('company')}", "Not Applied")
        options = ["Not Applied", "Applied", "Interviewing", "Saved"]
        default_index = options.index(current_status) if current_status in options else 0
        
        new_st = c2.selectbox("Status", options, index=default_index, key=f"st_{idx}")
        if new_st != current_status:
            update_job_status(job.get("title"), job.get("company"), new_st)
            st.rerun()

# --- Bottom Footer ---
st.markdown("""
<div class='footer-box'>
    ⚡ <b>SmartJobApply AI Engine Architected & Engineered by</b><br>
    <b style='color: #4f46e5; font-size: 1.05rem;'>Dongavath Pradeep</b>
</div>
""", unsafe_allow_html=True)
