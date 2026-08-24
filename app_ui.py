import os
import sqlite3
import pandas as pd
import streamlit as st

from resume_parser import parse_resume
from job_search import search_jobs
from email_notifier import send_email_alert
from db_manager import init_db, store_candidate_profile, get_candidate_profile, update_job_status, get_job_statuses
from semantic_matcher import calculate_semantic_fit
from ui_styles import CUSTOM_CSS

# --- Comprehensive Cross-Domain Job Roles Dataset ---
MASTER_JOB_ROLES = [
    "Python Developer", "Python Backend Developer", "Python Full Stack Developer",
    "Python Django / FastAPI Developer", "Python Data Engineer", "Python Machine Learning Engineer",
    "Python Automation Tester", "AI Engineer", "Generative AI Specialist", "Prompt Engineer",
    "NLP Engineer", "Computer Vision Engineer", "MLOps Engineer", "Java Developer",
    "Java Full Stack Developer", "Spring Boot Microservices Engineer", "Frontend Developer",
    "React.js Developer", "Angular Developer", "Node.js Developer", "Full Stack Web Developer",
    "Data Analyst", "Data Scientist", "DevOps Engineer", "Cloud Engineer (AWS/Azure/GCP)",
    "QA Automation Engineer", "Selenium Tester", "Cybersecurity Analyst", "SQL Developer"
]

# --- Page Configuration ---
st.set_page_config(page_title="Smart Job Finder | AI Career Intelligence", page_icon="⚡", layout="wide")
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
init_db()

# --- Custom Styling: Exact Hero Card Styling ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

/* IT Infrastructure Background */
.stApp {
    background-color: #0b0f19;
    background-image: 
        radial-gradient(at 0% 0%, rgba(56, 189, 248, 0.15) 0px, transparent 50%),
        radial-gradient(at 100% 0%, rgba(129, 140, 248, 0.15) 0px, transparent 50%),
        radial-gradient(at 50% 100%, rgba(192, 132, 252, 0.1) 0px, transparent 50%),
        linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
    background-size: 100% 100%, 100% 100%, 100% 100%, 40px 40px, 40px 40px;
}

/* Title Gradient */
.brand-title {
    background: linear-gradient(135deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2.2rem;
    font-weight: 800;
    margin: 0;
    letter-spacing: -0.5px;
}

/* Exact Large Hero Upload Box with Glowing Dotted Border */
.hero-ingest-container {
    background: linear-gradient(180deg, rgba(15, 23, 42, 0.95), rgba(11, 15, 25, 0.95));
    border: 1.5px dashed #0284c7;
    border-radius: 20px;
    padding: 35px 25px 25px 25px;
    margin: 15px 0 30px 0;
    box-shadow: 0 10px 35px rgba(0, 0, 0, 0.6), 0 0 25px rgba(2, 132, 199, 0.15);
    text-align: center;
}
.hero-ingest-title {
    color: #f8fafc;
    font-size: 1.75rem;
    font-weight: 700;
    margin: 0 0 8px 0;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
}
.hero-ingest-sub {
    color: #94a3b8;
    font-size: 0.98rem;
    margin: 0 0 20px 0;
}

/* Streamlit Native Uploader Custom Clean Dark Styling */
[data-testid="stFileUploader"] {
    background: rgba(30, 41, 59, 0.4);
    border-radius: 12px;
    padding: 10px;
    border: 1px solid rgba(56, 189, 248, 0.2);
}

/* Interactive Floating Step Cards */
.step-card {
    background: linear-gradient(145deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.9));
    border: 1px solid rgba(56, 189, 248, 0.2);
    border-radius: 14px;
    padding: 20px;
    height: 100%;
    text-align: left;
    transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    cursor: pointer;
}
.step-card:hover {
    transform: translateY(-8px) scale(1.03);
    border-color: #38bdf8;
    box-shadow: 0 12px 30px rgba(56, 189, 248, 0.25);
    background: linear-gradient(145deg, rgba(30, 41, 59, 0.95), rgba(15, 23, 42, 1));
}

.step-number {
    background: linear-gradient(135deg, #38bdf8, #818cf8);
    color: #0f172a;
    font-weight: 800;
    border-radius: 50%;
    width: 32px;
    height: 32px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 0.9rem;
    margin-bottom: 10px;
    box-shadow: 0 2px 8px rgba(56, 189, 248, 0.4);
}

/* Gradient Card */
.gradient-card {
    background: linear-gradient(145deg, rgba(30, 41, 59, 0.75), rgba(15, 23, 42, 0.9));
    border: 1px solid rgba(56, 189, 248, 0.25);
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 15px;
    box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    transition: transform 0.2s ease, border-color 0.2s ease;
}
.gradient-card:hover {
    border-color: #38bdf8;
    transform: translateY(-3px);
}

.gradient-badge-match {
    background: linear-gradient(135deg, #059669, #10b981);
    color: #ffffff;
    font-weight: 800;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.85rem;
    box-shadow: 0 2px 10px rgba(16, 185, 129, 0.3);
}

.tag-match { background: rgba(16, 185, 129, 0.15); border: 1px solid #10b981; color: #34d399; padding: 3px 9px; border-radius: 6px; font-size: 0.78rem; font-weight: 600; margin-right: 4px; display: inline-block; }
.tag-gap { background: rgba(239, 68, 68, 0.15); border: 1px solid #ef4444; color: #f87171; padding: 3px 9px; border-radius: 6px; font-size: 0.78rem; font-weight: 600; margin-right: 4px; display: inline-block; }
.role-suggestion-tag { display: inline-block; background: #1e293b; border: 1px solid #38bdf8; color: #38bdf8; padding: 4px 10px; margin: 4px 4px; border-radius: 6px; font-size: 0.82rem; font-family: monospace; }

/* Footer */
.footer-container {
    margin-top: 55px;
    padding: 25px;
    border-top: 1px solid rgba(51, 65, 85, 0.8);
    text-align: center;
    color: #94a3b8;
    font-size: 0.95rem;
    line-height: 1.6;
}
</style>
""", unsafe_allow_html=True)

# --- Top Header Section ---
st.markdown("""
<div style='padding-bottom:14px; border-bottom:1px solid #334155; margin-bottom: 20px;'>
    <h1 class='brand-title'>⚡ Smart Job Finder</h1>
    <p style='margin:0; color:#94a3b8; font-size:0.92rem;'>Next-Gen Semantic Vector Matcher & Autonomous Career Intelligence</p>
</div>
""", unsafe_allow_html=True)

# --- Sidebar Candidate Profile ---
with st.sidebar:
    st.markdown("<h3 style='color:#38bdf8;'>👤 Candidate Profile</h3>", unsafe_allow_html=True)
    profile = get_candidate_profile()
    if profile:
        skills = profile.get("skills", [])
        ats = min(95, max(50, len(skills) * 12)) if skills else 30
        st.metric("Neural ATS Score", f"{ats}/100")
        st.progress(ats / 100)
        
        c_name = profile.get('full_name') or "PRADEEP NAIK DONGAVATH"
        c_email = profile.get('email') or "dungavathpradeepnaik123@gmail.com"
        
        st.markdown(f"**Name:** `{c_name}`")
        st.markdown(f"**Email:** <br><code style='color:#34d399; font-size:0.8rem;'>{c_email}</code>", unsafe_allow_html=True)
        st.markdown("<div style='margin-top:10px;'><b>Extracted Skills:</b></div>", unsafe_allow_html=True)
        st.markdown("".join([f"<span class='tag-match'>{s}</span>" for s in skills]), unsafe_allow_html=True)
    else:
        st.info("No active candidate profile. Ingest your resume on the Home page to initialize.")

    st.markdown("<hr style='border:0.5px solid #334155; margin-top:25px;'>", unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align: center; color: #94a3b8; font-size: 0.85rem;'>
        <b>System Architect</b><br>
        <span style='color: #38bdf8; font-weight: bold;'>Dongavath Pradeep</span><br><br>
        <a href='https://github.com/DongavathPradeep' target='_blank' style='color:#38bdf8; text-decoration:none; font-weight:600;'>🔗 GitHub Profile</a><br>
        <a href='https://www.linkedin.com/in/pradeep-naik-42292b264/' target='_blank' style='color:#38bdf8; text-decoration:none; font-weight:600;'>💼 LinkedIn Profile</a>
    </div>
    """, unsafe_allow_html=True)

# --- Navigation Tabs ---
tab_home, tab_features, tab_about, tab_tracker, tab_alerts = st.tabs([
    "🏠 Home", "⭐ Features", "💡 About Project", "📋 Application Tracker", "📬 Email Alerts"
])

if "jobs_data" not in st.session_state:
    st.session_state["jobs_data"] = []

# ========================================================
# 1. TAB: HOME (Exact Unified Hero Upload Box)
# ========================================================
with tab_home:
    # Exact Large Dotted-Border Hero Card Container
    st.markdown("""
    <div class='hero-ingest-container'>
        <div class='hero-ingest-title'>
            <span>📄</span> Ingest Candidate Resume
        </div>
        <p class='hero-ingest-sub'>
            Upload your PDF resume to generate dense vector embeddings and extract skill matrices.
        </p>
    """, unsafe_allow_html=True)

    up_c1, up_c2, up_c3 = st.columns([1, 2.8, 1])
    with up_c2:
        uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"], label_visibility="collapsed")
        if uploaded_file and st.button("🚀 Process & Build Embeddings", use_container_width=True):
            temp_path = f"temp_{uploaded_file.name}"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            try:
                parsed_data = parse_resume(temp_path)
                store_candidate_profile(parsed_data)
                st.success("✅ Resume parsed and candidate embeddings initialized successfully!")
                st.rerun()
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

    st.markdown("</div>", unsafe_allow_html=True)

    # Interactive Floating Steps (Movement on Cursor Hover)
    st.markdown("<h4 style='color:#38bdf8; text-align:center; margin: 30px 0 18px 0;'>🧭 How Smart Job Finder Fetches Your Best Matches</h4>", unsafe_allow_html=True)
    s1, s2, s3, s4 = st.columns(4)

    with s1:
        st.markdown("""
        <div class='step-card'>
            <div class='step-number'>1</div>
            <h5 style='color:#f8fafc; margin:0 0 6px 0;'>1. Extract & Vectorize</h5>
            <p style='color:#94a3b8; font-size:0.83rem; margin:0;'>Parses PDF text, extracts technical skills, years of experience, and converts into semantic vector embeddings.</p>
        </div>
        """, unsafe_allow_html=True)

    with s2:
        st.markdown("""
        <div class='step-card'>
            <div class='step-number'>2</div>
            <h5 style='color:#f8fafc; margin:0 0 6px 0;'>2. Real-Time Fetching</h5>
            <p style='color:#94a3b8; font-size:0.83rem; margin:0;'>Searches active job openings across major hubs like Hyderabad, Bangalore, and remote domains dynamically.</p>
        </div>
        """, unsafe_allow_html=True)

    with s3:
        st.markdown("""
        <div class='step-card'>
            <div class='step-number'>3</div>
            <h5 style='color:#f8fafc; margin:0 0 6px 0;'>3. Semantic Cosine Score</h5>
            <p style='color:#94a3b8; font-size:0.83rem; margin:0;'>Calculates contextual similarity between your resume and Job Descriptions to produce an accurate Match Score.</p>
        </div>
        """, unsafe_allow_html=True)

    with s4:
        st.markdown("""
        <div class='step-card'>
            <div class='step-number'>4</div>
            <h5 style='color:#f8fafc; margin:0 0 6px 0;'>4. Skill Gap & 1-Click Apply</h5>
            <p style='color:#94a3b8; font-size:0.83rem; margin:0;'>Highlights missing framework requirements, provides direct apply portals, and logs applications to SQLite.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='border:0.5px solid #334155; margin: 30px 0;'>", unsafe_allow_html=True)

    # Live Job Matching Section
    st.markdown("<h4 style='color:#f8fafc;'>🎯 Live Neural Job Matching Feed</h4>", unsafe_allow_html=True)
    candidate_skills = profile.get("skills", []) if profile else []
    default_role = ", ".join(candidate_skills[:3]) if candidate_skills else "Python, SQL, Machine Learning"

    col1, col2, col3, col4 = st.columns([2.2, 1.1, 1.1, 0.9])
    role_query = col1.text_input("Target Role / Skills (Loaded from Resume)", value=default_role)
    exp_level = col2.selectbox("Experience", ["Fresher / Entry Level", "1-3 yrs", "4+ yrs", "All"])
    location_query = col3.selectbox("Location", ["Hyderabad", "Bangalore", "Pune", "Chennai", "Remote"])

    if role_query.strip():
        matching_roles = [r for r in MASTER_JOB_ROLES if role_query.strip().lower() in r.lower()]
        if matching_roles:
            tags_html = "".join([f"<span class='role-suggestion-tag'>{r}</span>" for r in matching_roles])
            st.markdown(f"<div style='margin-top:-10px; margin-bottom:12px;'><small style='color:#94a3b8;'><b>Associated Market Roles:</b></small><br>{tags_html}</div>", unsafe_allow_html=True)

    if col4.button("🚀 Fetch Matches", use_container_width=True):
        if not profile:
            st.warning("⚠️ Please upload your resume first using the upload box above!")
        else:
            with st.spinner(f"Matching live jobs for '{role_query}'..."):
                raw = search_jobs(role=role_query, location=location_query)
                st.session_state["jobs_data"] = calculate_semantic_fit(profile, raw)

    results = st.session_state.get("jobs_data", [])
    statuses = get_job_statuses()

    if results:
        m1, m2, m3 = st.columns(3)
        m1.metric("Roles Evaluated", len(results))
        avg_score = round(sum([j.get("semantic_score", 0) for j in results]) / len(results), 1)
        m2.metric("Mean Semantic Match", f"{avg_score}%")
        m3.metric("High Match Roles (≥70%)", len([j for j in results if j.get("semantic_score", 0) >= 70]))

        for idx, job in enumerate(results):
            matched_html = "".join([f"<span class='tag-match'>✓ {s}</span>" for s in job.get("matched_skills", [])]) or "None detected"
            missing_html = "".join([f"<span class='tag-gap'>✗ {s}</span>" for s in job.get("missing_skills", [])]) or "<span style='color:#34d399;'>None</span>"

            st.markdown(f"""
            <div class='gradient-card'>
                <div style='display:flex; justify-content:space-between; align-items:center;'>
                    <h4 style='color:#38bdf8; margin:0;'>{job.get('title')}</h4>
                    <span class='gradient-badge-match'>{job.get('semantic_score')}% Match</span>
                </div>
                <p style='color:#cbd5e1; font-size:0.88rem; margin:4px 0 10px 0;'><b>{job.get('company')}</b> • {job.get('location')}</p>
                <div style='margin-bottom:6px;'><b>Matched Skills:</b> {matched_html}</div>
                <div><b>Skill Gaps:</b> {missing_html}</div>
            </div>
            """, unsafe_allow_html=True)

            c1, c2 = st.columns([3, 1])
            if job.get("url"):
                c1.markdown(f"[🚀 **Apply via Portal**]({job.get('url')})")

            current_status = statuses.get(f"{job.get('title')}--{job.get('company')}", "Not Applied")
            options = ["Not Applied", "Applied", "Interviewing", "Saved"]
            default_index = options.index(current_status) if current_status in options else 0

            new_st = c2.selectbox("Status", options, index=default_index, key=f"st_{idx}")
            if new_st != current_status:
                update_job_status(job.get("title"), job.get("company"), new_st)
                st.rerun()

# ========================================================
# 2. TAB: FEATURES
# ========================================================
with tab_features:
    st.markdown("<h3 style='color:#38bdf8;'>⭐ Smart Job Finder Features</h3>", unsafe_allow_html=True)
    f1, f2 = st.columns(2)
    with f1:
        st.markdown("""
        #### 🎯 1. Contextual AI Matching
        * Bypasses simple keyword searches by evaluating full semantic context between candidate resumes and live industry requirements.
        
        #### 🔍 2. Live Skill Gap Detection
        * Instantly pinpoints missing frameworks (e.g., Docker, FastAPI, Kubernetes) to help candidates prepare before attending interviews.
        """)
    with f2:
        st.markdown("""
        #### 📋 3. Built-In Application Lifecycle Tracker
        * Seamlessly tracks statuses (`Saved`, `Applied`, `Interviewing`) across job postings with zero data loss using local SQLite.

        #### 📬 4. Instant Digest Email Alerts
        * Dispatches curated lists of high-scoring job matches straight to the user's verified email inbox.
        """)

# ========================================================
# 3. TAB: ABOUT PROJECT
# ========================================================
with tab_about:
    st.markdown("<h3 style='color:#38bdf8;'>💡 What is Smart Job Finder & What Does It Do?</h3>", unsafe_allow_html=True)
    st.markdown("""
    **Smart Job Finder** is an autonomous AI career co-pilot engineered to take the guesswork out of job hunting. Instead of spending hours sending generic applications with low response rates, it deeply analyzes candidate experience and aligns them with ideal market roles.
    """)
    
    ab1, ab2 = st.columns(2)
    with ab1:
        st.markdown("""
        <div class='gradient-card'>
            <h4 style='color:#38bdf8; margin-top:0;'>🎯 Finds True Semantic Match</h4>
            <p style='color:#cbd5e1; font-size:0.88rem; margin:0;'>
                Matches your background contextually with active market requirements, moving beyond rigid word-by-word filtering.
            </p>
        </div>
        <div class='gradient-card'>
            <h4 style='color:#34d399; margin-top:0;'>⚡ High-Confidence Applications</h4>
            <p style='color:#cbd5e1; font-size:0.88rem; margin:0;'>
                Provides an instant Match Score before applying so you can focus on roles where you have the highest probability of receiving interview callbacks.
            </p>
        </div>
        """, unsafe_allow_html=True)
    with ab2:
        st.markdown("""
        <div class='gradient-card'>
            <h4 style='color:#f59e0b; margin-top:0;'>🔍 Clear Skill Gap Analysis</h4>
            <p style='color:#cbd5e1; font-size:0.88rem; margin:0;'>
                Identifies missing tools and technologies for specific openings, empowering targeted upskilling.
            </p>
        </div>
        <div class='gradient-card'>
            <h4 style='color:#c084fc; margin-top:0;'>📋 Unified Search Organization</h4>
            <p style='color:#cbd5e1; font-size:0.88rem; margin:0;'>
                Manages every application status in one place, streamlining the entire job search process.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='border:0.5px solid #334155;'>", unsafe_allow_html=True)
    st.markdown("""
    <div style='background:rgba(30, 41, 59, 0.7); border:1px solid #38bdf8; border-radius:12px; padding:20px; text-align:center;'>
        <h4 style='color:#f8fafc; margin:0;'>👨‍💻 System Architect & Engineer</h4>
        <h3 style='color:#38bdf8; margin:6px 0 12px 0;'>Dongavath Pradeep</h3>
        <p style='color:#cbd5e1; font-size:0.9rem; max-width:600px; margin:0 auto 15px auto;'>
            Engineered to empower job seekers with transparent AI matching, instant skill gap analysis, and automated job discovery.
        </p>
        <a href='https://github.com/DongavathPradeep' target='_blank' style='background:#0f172a; border:1px solid #38bdf8; color:#38bdf8; padding:8px 16px; border-radius:8px; text-decoration:none; font-weight:600; margin-right:10px;'>🔗 GitHub Profile</a>
        <a href='https://www.linkedin.com/in/pradeep-naik-42292b264/' target='_blank' style='background:#0284c7; color:white; padding:8px 16px; border-radius:8px; text-decoration:none; font-weight:600;'>💼 LinkedIn Profile</a>
    </div>
    """, unsafe_allow_html=True)

# ========================================================
# 4. TAB: APPLICATION TRACKER
# ========================================================
with tab_tracker:
    st.markdown("<h3 style='color:#38bdf8;'>📋 Real-Time Application Tracker</h3>", unsafe_allow_html=True)
    conn = sqlite3.connect("candidate.db")
    df_track = pd.read_sql("SELECT job_title AS 'Role', company AS 'Company', status AS 'Status', updated_at AS 'Updated' FROM applications", conn)
    conn.close()
    if not df_track.empty:
        st.dataframe(df_track, use_container_width=True)
    else:
        st.info("No applications logged yet. Search jobs on the Home tab and update their status!")

# ========================================================
# 5. TAB: EMAIL ALERTS
# ========================================================
with tab_alerts:
    st.markdown("<h3 style='color:#38bdf8;'>📬 Automated Email Gateway</h3>", unsafe_allow_html=True)
    if profile:
        target_email = profile.get("email") or "dungavathpradeepnaik123@gmail.com"
        target_name = profile.get("full_name") or "Pradeep Naik"
        
        st.markdown(f"**Target Candidate:** `{target_name}`")
        st.markdown(f"**Destination Inbox:** `<span style='color:#34d399;'>{target_email}</span>`", unsafe_allow_html=True)
        st.markdown(f"**Queued Matched Roles:** `{len(st.session_state.get('jobs_data', []))}`")
        
        if st.button("🚀 Trigger Email Digest Now", use_container_width=True):
            current_jobs = st.session_state.get("jobs_data", [])
            if current_jobs:
                with st.spinner("Dispatching email digest via SMTP..."):
                    success = send_email_alert(target_email, target_name, current_jobs)
                    if success:
                        st.success(f"✅ High-match job digest successfully sent to {target_email}!")
                    else:
                        st.error("❌ Failed to send email. Check your SMTP configuration.")
            else:
                st.warning("⚠️ No jobs in queue! Fetch jobs in the Home tab first.")
    else:
        st.warning("⚠️ Please upload your resume in the Home tab to initialize candidate profile.")

# --- Bottom Footer ---
st.markdown("""
<div class='footer-container'>
    ⚡ <b>Smart Job Finder Architected & Engineered by</b><br>
    <b style='color: #38bdf8; font-size: 1.05rem;'>Dongavath Pradeep</b>
</div>
""", unsafe_allow_html=True)
