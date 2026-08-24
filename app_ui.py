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
    # Python & AI
    "Python Developer", "Python Backend Developer", "Python Full Stack Developer",
    "Python Django / FastAPI Developer", "Python Data Engineer", "Python Machine Learning Engineer",
    "Python Automation Tester", "AI Engineer", "Generative AI Specialist", "Prompt Engineer",
    "NLP Engineer", "Computer Vision Engineer", "MLOps Engineer",

    # Java Ecosystem
    "Java Developer", "Java Full Stack Developer", "Java Spring Boot Microservices Engineer",
    "Java Backend Architect", "Core Java Developer",

    # Frontend & Full Stack
    "Frontend Developer", "React.js Developer", "Angular Developer", "Vue.js Developer",
    "Node.js Backend Developer", "Full Stack Web Developer", "MERN Stack Developer",
    "MEAN Stack Developer", "Next.js Full Stack Engineer", "UI/UX Developer",

    # Data Science & Analytics
    "Data Analyst", "Data Scientist", "Business Intelligence (BI) Analyst",
    "Power BI / Tableau Developer", "Big Data Engineer (Spark/Hadoop)", "Snowflake Data Engineer",

    # Cloud & DevOps
    "DevOps Engineer", "Cloud Engineer (AWS/Azure/GCP)", "Kubernetes / Docker Specialist",
    "Site Reliability Engineer (SRE)", "Terraform Infrastructure Engineer", "Linux System Administrator",

    # QA & Testing
    "QA Automation Engineer", "Selenium Automation Tester", "Manual QA Tester",
    "Performance Test Engineer (JMeter)", "API Testing Specialist (Postman)",

    # Mobile & Databases
    "Android Developer (Kotlin)", "iOS Developer (Swift)", "Flutter Mobile Engineer", "React Native Developer",
    "Cybersecurity Analyst", "SQL / Database Administrator (DBA)", "PostgreSQL Backend Developer"
]

# --- Page Configuration ---
st.set_page_config(page_title="JobNexus | AI Vector Career Intelligence", page_icon="⚡", layout="wide")
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
init_db()

# --- Custom Styling for Unified Card & UI ---
st.markdown("""
<style>
.footer-container {
    margin-top: 50px;
    padding: 20px;
    border-top: 1px solid #334155;
    text-align: center;
    color: #94a3b8;
    font-size: 0.95rem;
    line-height: 1.6;
}
.role-suggestion-tag {
    display: inline-block;
    background: #1e293b;
    border: 1px solid #38bdf8;
    color: #38bdf8;
    padding: 4px 10px;
    margin: 4px 4px;
    border-radius: 6px;
    font-size: 0.82rem;
    font-family: monospace;
}
.unified-upload-box {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.9));
    border: 1.5px dashed #38bdf8;
    border-radius: 16px;
    padding: 28px 24px 20px 24px;
    margin: 10px 0 25px 0;
    box-shadow: 0 4px 24px rgba(56, 189, 248, 0.08);
}
.step-card {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 18px;
    height: 100%;
    text-align: left;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}
.step-number {
    background: #38bdf8;
    color: #0f172a;
    font-weight: 800;
    border-radius: 50%;
    width: 28px;
    height: 28px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 0.85rem;
    margin-bottom: 8px;
}
.about-card {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 16px;
}
</style>
""", unsafe_allow_html=True)

# --- Top Header Section ---
st.markdown("""
<div style='display:flex; justify-content:space-between; align-items:center; padding-bottom:14px; border-bottom:1px solid #334155;'>
    <div>
        <h2 style='margin:0; color:#f8fafc; font-size:1.6rem;'>⚡ JobNexus Neural Console</h2>
        <p style='margin:0; color:#94a3b8; font-size:0.9rem;'>Vector Embeddings & Semantic Skill Gap Architecture</p>
    </div>
    <div style='display: flex; gap: 8px;'>
        <span style='background:#1e293b; border:1px solid #38bdf8; color:#38bdf8; font-family:monospace; padding:6px 10px; border-radius:6px; font-size: 0.8rem;'>EMBEDDINGS: all-MiniLM-L6-v2</span>
        <span style='background:#1e293b; border:1px solid #34d399; color:#34d399; font-family:monospace; padding:6px 10px; border-radius:6px; font-size: 0.8rem;'>SQLITE PROD</span>
    </div>
</div>
""", unsafe_allow_html=True)

# --- Sidebar Quick Info & Branding ---
with st.sidebar:
    st.markdown("<h3 style='color:#38bdf8;'>👤 Candidate Profile</h3>", unsafe_allow_html=True)
    profile = get_candidate_profile()
    if profile:
        skills = profile.get("skills", [])
        ats = min(95, max(50, len(skills) * 12)) if skills else 30
        st.metric("Neural ATS Alignment", f"{ats}/100")
        st.progress(ats / 100)
        st.markdown(f"**Name:** `{profile.get('full_name')}`\n\n**Email:** `{profile.get('email')}`")
        st.markdown("".join([f"<span class='tag-match'>{s}</span>" for s in skills]), unsafe_allow_html=True)
    else:
        st.info("No active candidate profile loaded. Upload your resume in the Home page to initialize vectors.")

    st.markdown("<hr style='border:0.5px solid #334155; margin-top:30px;'>", unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align: center; color: #94a3b8; font-size: 0.85rem;'>
        <b>System Architect</b><br>
        <span style='color: #38bdf8; font-weight: bold;'>Dongavath Pradeep</span><br><br>
        <a href='https://github.com/DongavathPradeep' target='_blank' style='color:#38bdf8; text-decoration:none; font-weight:600;'>🔗 GitHub Profile</a><br>
        <a href='https://www.linkedin.com/in/pradeep-naik-42292b264/' target='_blank' style='color:#38bdf8; text-decoration:none; font-weight:600;'>💼 LinkedIn Profile</a>
    </div>
    """, unsafe_allow_html=True)

# --- Main Navigation Tabs ---
tab_home, tab_features, tab_about = st.tabs(["🏠 Home", "⚡ Features", "💡 About Project"])

# ==========================================
# 1. HOME TAB (Single Unified Upload Box -> Steps -> Search)
# ==========================================
with tab_home:
    # Single Box for Header, Subtitle & Uploader
    st.markdown("""
    <div class='unified-upload-box'>
        <div style='text-align: center;'>
            <h3 style='margin:0; color:#f8fafc;'>📄 Ingest Candidate Resume</h3>
            <p style='color:#94a3b8; font-size:0.9rem; margin:6px 0 16px 0;'>
                Upload your PDF resume to generate 384-dimensional vector embeddings and extract skill matrices.
            </p>
        </div>
    """, unsafe_allow_html=True)

    up_c1, up_c2, up_c3 = st.columns([1, 2.2, 1])
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

    # 4-Step Guide: How to Fetch & Match Your Target Jobs
    st.markdown("<h4 style='color:#38bdf8; text-align:center; margin: 30px 0 18px 0;'>🧭 How to Fetch & Match Your Target Jobs</h4>", unsafe_allow_html=True)
    s1, s2, s3, s4 = st.columns(4)

    with s1:
        st.markdown("""
        <div class='step-card'>
            <div class='step-number'>1</div>
            <h5 style='color:#f8fafc; margin:0 0 6px 0;'>Ingest Resume</h5>
            <p style='color:#94a3b8; font-size:0.82rem; margin:0;'>Upload your PDF above. NLP extracts tech skills, experience, and contact metadata.</p>
        </div>
        """, unsafe_allow_html=True)

    with s2:
        st.markdown("""
        <div class='step-card'>
            <div class='step-number'>2</div>
            <h5 style='color:#f8fafc; margin:0 0 6px 0;'>Keyword Live Search</h5>
            <p style='color:#94a3b8; font-size:0.82rem; margin:0;'>Type your target skill/role below to see related industry domains and live postings.</p>
        </div>
        """, unsafe_allow_html=True)

    with s3:
        st.markdown("""
        <div class='step-card'>
            <div class='step-number'>3</div>
            <h5 style='color:#f8fafc; margin:0 0 6px 0;'>Semantic Match & Gaps</h5>
            <p style='color:#94a3b8; font-size:0.82rem; margin:0;'>The neural engine computes cosine similarity between your resume and Job Descriptions.</p>
        </div>
        """, unsafe_allow_html=True)

    with s4:
        st.markdown("""
        <div class='step-card'>
            <div class='step-number'>4</div>
            <h5 style='color:#f8fafc; margin:0 0 6px 0;'>Apply & Track</h5>
            <p style='color:#94a3b8; font-size:0.82rem; margin:0;'>Apply directly via portals, update application status, and trigger SMTP email alerts.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='border:0.5px solid #334155; margin: 30px 0;'>", unsafe_allow_html=True)

    # Job Search & Live Vector Matching
    st.markdown("<h4 style='color:#f8fafc;'>🎯 Live Neural Job Search Feed</h4>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns([2.2, 1.1, 1.1, 0.8])
    
    if "role_input" not in st.session_state:
        st.session_state["role_input"] = "Python"

    role_query = col1.text_input(
        "Target Role / Skill Keyword", 
        value=st.session_state["role_input"],
        help="Type any keyword (e.g., Python, Java, React, Data, Cloud) to see related market roles"
    )
    
    exp_level = col2.selectbox("Experience", ["Fresher / Entry Level", "1-3 yrs", "4+ yrs", "All"])
    location_query = col3.selectbox("Location", ["Hyderabad", "Bangalore", "Pune", "Chennai", "Remote"])
    
    # Associated Live Roles Tags Display
    if role_query.strip():
        matching_roles = [r for r in MASTER_JOB_ROLES if role_query.strip().lower() in r.lower()]
        if matching_roles:
            tags_html = "".join([f"<span class='role-suggestion-tag'>{r}</span>" for r in matching_roles])
            st.markdown(f"<div style='margin-top:-10px; margin-bottom:12px;'><small style='color:#94a3b8;'><b>Associated Market Roles:</b></small><br>{tags_html}</div>", unsafe_allow_html=True)

    if "jobs_data" not in st.session_state:
        st.session_state["jobs_data"] = []

    active_candidate = get_candidate_profile()

    if col4.button("Run Vector Match", use_container_width=True):
        if not active_candidate:
            st.warning("⚠️ Please upload your resume first using the upload box above!")
        else:
            with st.spinner(f"Computing cosine distance for '{role_query}' across live JD embeddings..."):
                raw = search_jobs(role=role_query, location=location_query)
                st.session_state["jobs_data"] = calculate_semantic_fit(active_candidate, raw)

    results = st.session_state.get("jobs_data", [])
    statuses = get_job_statuses()
    
    if results:
        m1, m2, m3 = st.columns(3)
        m1.metric("Roles Evaluated", len(results))
        avg_score = round(sum([j.get("semantic_score", 0) for j in results]) / len(results), 1)
        m2.metric("Mean Semantic Similarity", f"{avg_score}%")
        m3.metric("High Semantic Fit (≥70%)", len([j for j in results if j.get("semantic_score", 0) >= 70]))
        
        for idx, job in enumerate(results):
            matched_html = "".join([f"<span class='tag-match'>✓ {s}</span>" for s in job.get("matched_skills", [])]) or "None detected"
            missing_html = "".join([f"<span class='tag-gap'>✗ {s}</span>" for s in job.get("missing_skills", [])]) or "<span style='color:#34d399;'>None</span>"
            
            st.markdown(f"""
            <div class='job-card'>
                <div style='display:flex; justify-content:space-between;'>
                    <h4 style='color:#38bdf8; margin:0;'>{job.get('title')}</h4>
                    <span style='color:#34d399; font-weight:800;'>{job.get('semantic_score')}% Semantic Match</span>
                </div>
                <p style='color:#cbd5e1; font-size:0.88rem;'><b>{job.get('company')}</b> • {job.get('location')}</p>
                <div style='margin-bottom:6px;'><b>Direct Matches:</b> {matched_html}</div>
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

# ==========================================
# 2. FEATURES TAB
# ==========================================
with tab_features:
    st.markdown("<h3 style='color:#38bdf8;'>⚡ Platform Features & Capabilities</h3>", unsafe_allow_html=True)
    
    f1, f2 = st.columns(2)
    with f1:
        st.markdown("""
        #### 🎯 1. Contextual AI Matching
        * Moves beyond simple keyword search. It understands candidate experience context and pairs it with real job requirements.
        
        #### 🔍 2. Live Skill Gap Detection
        * Instantly shows what skills match the job description and what specific tools are missing so candidates can prepare before interviewing.
        """)
    with f2:
        st.markdown("""
        #### 📋 3. Built-in Application Tracker
        * Easily manage all your active job applications in one place without needing external spreadsheets or notes.

        #### 📬 4. Instant Digest Alerts
        * Get curated lists of top matching jobs delivered straight to your email with a single click.
        """)

    st.markdown("<hr style='border:0.5px solid #334155;'>", unsafe_allow_html=True)
    
    st.markdown("#### 📊 Real-Time Application Tracker")
    conn = sqlite3.connect("candidate.db")
    df = pd.read_sql("SELECT job_title AS 'Role', company AS 'Company', status AS 'Status', updated_at AS 'Updated' FROM applications", conn)
    conn.close()
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No applications logged yet. Search jobs in the Home tab and update their status!")

# ==========================================
# 3. ABOUT TAB (What JobNexus Does & User Benefits)
# ==========================================
with tab_about:
    st.markdown("<h3 style='color:#38bdf8;'>💡 What is JobNexus & What Does It Do?</h3>", unsafe_allow_html=True)
    
    st.markdown("""
    **JobNexus** is an AI-powered Career Co-Pilot designed to take the guesswork out of job hunting. Instead of spending hours applying randomly to hundreds of job postings with low response rates, JobNexus analyzes your exact resume and pairs you with the most relevant opportunities.
    """)

    ab1, ab2 = st.columns(2)
    with ab1:
        st.markdown("""
        <div class='about-card'>
            <h4 style='color:#38bdf8; margin-top:0;'>🎯 1. Finds Your True Semantic Fit</h4>
            <p style='color:#cbd5e1; font-size:0.88rem; margin:0;'>
                Traditional portals only look for matching words. JobNexus understands your technical experience depth, matching your background contextually with real market requirements.
            </p>
        </div>
        <div class='about-card'>
            <h4 style='color:#34d399; margin-top:0;'>⚡ 2. Eliminates Resume Rejections</h4>
            <p style='color:#cbd5e1; font-size:0.88rem; margin:0;'>
                By giving you an instant <b>Match Score (e.g., 85%)</b> before you apply, you know exactly which jobs you have the highest probability of getting an interview call for.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with ab2:
        st.markdown("""
        <div class='about-card'>
            <h4 style='color:#f59e0b; margin-top:0;'>🔍 3. Identifies Critical Skill Gaps</h4>
            <p style='color:#cbd5e1; font-size:0.88rem; margin:0;'>
                It tells you what tools or technologies you are missing for a specific job (e.g., Docker, FastAPI, Kubernetes), allowing you to upskill quickly before an interview.
            </p>
        </div>
        <div class='about-card'>
            <h4 style='color:#a855f7; margin-top:0;'>📋 4. Organizes Your Entire Job Search</h4>
            <p style='color:#cbd5e1; font-size:0.88rem; margin:0;'>
                Tracks every application from 'Saved' to 'Interviewing' and 'Applied' in one unified database, keeping your job search structured and stress-free.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<hr style='border:0.5px solid #334155;'>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style='background:#1e293b; border:1px solid #38bdf8; border-radius:12px; padding:20px; text-align:center;'>
        <h4 style='color:#f8fafc; margin:0;'>👨‍💻 System Architect & Engineer</h4>
        <h3 style='color:#38bdf8; margin:6px 0 12px 0;'>Dongavath Pradeep</h3>
        <p style='color:#cbd5e1; font-size:0.9rem; max-width:600px; margin:0 auto 15px auto;'>
            Engineered to empower developers and job seekers with modern AI matching tools, transparent skill insights, and efficient career navigation.
        </p>
        <a href='https://github.com/DongavathPradeep' target='_blank' style='background:#0f172a; border:1px solid #38bdf8; color:#38bdf8; padding:8px 16px; border-radius:8px; text-decoration:none; font-weight:600; margin-right:10px;'>🔗 GitHub Profile</a>
        <a href='https://www.linkedin.com/in/pradeep-naik-42292b264/' target='_blank' style='background:#0284c7; color:white; padding:8px 16px; border-radius:8px; text-decoration:none; font-weight:600;'>💼 LinkedIn Profile</a>
    </div>
    """, unsafe_allow_html=True)

# --- Bottom Footer (2 Lines) ---
st.markdown("""
<div class='footer-container'>
    ⚡ <b>JobNexus AI Engine Architected & Engineered by</b><br>
    <b style='color: #38bdf8; font-size: 1.05rem;'>Dongavath Pradeep</b>
</div>
""", unsafe_allow_html=True)
