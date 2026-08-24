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

    # Mobile Development
    "Android Developer (Kotlin)", "iOS Developer (Swift)", "Flutter Mobile Engineer", "React Native Developer",

    # Cybersecurity & Databases
    "Cybersecurity Analyst", "Information Security Specialist", "SOC Analyst", "Penetration Tester",
    "SQL / Database Administrator (DBA)", "PostgreSQL Backend Developer", "Oracle PL/SQL Developer",
    "SAP ABAP Consultant", "Salesforce Developer"
]

# --- Page Configuration ---
st.set_page_config(page_title="JobNexus | AI Vector Career Intelligence", page_icon="⚡", layout="wide")
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
init_db()

# --- Custom Styling for Footer & Tags ---
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

# --- Sidebar Candidate Ingestion & Info ---
with st.sidebar:
    st.markdown("<h3 style='color:#38bdf8;'>📄 Candidate Ingestion</h3>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload PDF Resume", type=["pdf"])
    if uploaded_file and st.button("Parse & Generate Embeddings", use_container_width=True):
        temp_path = f"temp_{uploaded_file.name}"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        try:
            store_candidate_profile(parse_resume(temp_path))
            st.success("Candidate vectors stored & initialized.")
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
    st.markdown("<hr style='border:0.5px solid #334155;'>", unsafe_allow_html=True)
    profile = get_candidate_profile()
    if profile:
        skills = profile.get("skills", [])
        ats = min(95, max(50, len(skills) * 12)) if skills else 30
        st.metric("Neural ATS Alignment", f"{ats}/100")
        st.progress(ats / 100)
        
        c_name = profile.get('full_name') or "PRADEEP NAIK DONGAVATH"
        c_email = profile.get('email') or "dungavathpradeepnaik123@gmail.com"
        
        st.markdown(f"**Candidate:** `{c_name}`\n\n**Contact:** `{c_email}`")
        st.markdown("".join([f"<span class='tag-match'>{s}</span>" for s in skills]), unsafe_allow_html=True)

    # Sidebar Developer Tag
    st.markdown("<hr style='border:0.5px solid #334155; margin-top:30px;'>", unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align: center; color: #94a3b8; font-size: 0.85rem;'>
        <b>System Architect</b><br>
        <span style='color: #38bdf8; font-weight: bold;'>Dongavath Pradeep</span><br><br>
        <a href='https://github.com/DongavathPradeep' target='_blank' style='color:#38bdf8; text-decoration:none; font-weight:600;'>🔗 GitHub Profile</a><br>
        <a href='https://www.linkedin.com/in/pradeep-naik-42292b264/' target='_blank' style='color:#38bdf8; text-decoration:none; font-weight:600;'>💼 LinkedIn Profile</a>
    </div>
    """, unsafe_allow_html=True)

# --- 5 Navigation Tabs (Original Setup) ---
tab_feed, tab_analytics, tab_roadmap, tab_tracker, tab_alerts = st.tabs([
    "🎯 Neural Job Feed", "📊 Gap Intelligence", "🗺️ 7-Day Bridge Roadmap", "📋 Application Tracker", "📬 Automation & SMTP"
])

if "jobs_data" not in st.session_state:
    st.session_state["jobs_data"] = []
if "role_input" not in st.session_state:
    st.session_state["role_input"] = "Python"

# 1. TAB: FEED
with tab_feed:
    col1, col2, col3, col4 = st.columns([2.2, 1.1, 1.1, 0.8])
    role_query = col1.text_input(
        "Target Role / Keyword", 
        value=st.session_state["role_input"],
        help="Type any keyword (e.g., Python, Java, React, Data, Cloud) to see related market roles"
    )
    
    exp_level = col2.selectbox("Experience", ["Fresher / Entry Level", "1-3 yrs", "4+ yrs", "All"])
    location_query = col3.selectbox("Location", ["Hyderabad", "Bangalore", "Pune", "Chennai", "Remote"])
    
    # Associated Dynamic Role Tags
    if role_query.strip():
        matching_roles = [r for r in MASTER_JOB_ROLES if role_query.strip().lower() in r.lower()]
        if matching_roles:
            tags_html = "".join([f"<span class='role-suggestion-tag'>{r}</span>" for r in matching_roles])
            st.markdown(f"<div style='margin-top:-10px; margin-bottom:12px;'><small style='color:#94a3b8;'><b>Associated Market Roles:</b></small><br>{tags_html}</div>", unsafe_allow_html=True)

    if col4.button("Run Vector Match", use_container_width=True):
        if not profile:
            st.warning("⚠️ Please upload your resume in the sidebar first!")
        else:
            with st.spinner(f"Computing cosine distance for '{role_query}' across live JD embeddings..."):
                raw = search_jobs(role=role_query, location=location_query)
                st.session_state["jobs_data"] = calculate_semantic_fit(profile, raw)

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

# 2. TAB: GAP INTELLIGENCE
with tab_analytics:
    if results:
        all_miss = [s for j in results for s in j.get("missing_skills", [])]
        if all_miss: 
            st.caption("Top Missing Market Skills by Vector Frequency")
            st.bar_chart(pd.Series(all_miss).value_counts().head(8))
        else: 
            st.success("High semantic vector alignment across all skills!")
    else:
        st.info("Run a job search in the first tab to view skill gap analytics.")

# 3. TAB: ROADMAP
with tab_roadmap:
    st.markdown("#### 🗺️ 7-Day Targeted Upskilling Bridge")
    st.write("Day 1-2: Vector Foundations | Day 3-4: Build API | Day 5-6: Containerization | Day 7: Resume Re-indexing")

# 4. TAB: TRACKER
with tab_tracker:
    conn = sqlite3.connect("candidate.db")
    df_track = pd.read_sql("SELECT job_title AS 'Role', company AS 'Company', status AS 'Status', updated_at AS 'Updated' FROM applications", conn)
    conn.close()
    if not df_track.empty:
        st.dataframe(df_track, use_container_width=True)
    else:
        st.info("No applications logged yet.")

# 5. TAB: AUTOMATION & SMTP (Email Dispatcher)
with tab_alerts:
    st.markdown("### 📬 Email Automation & SMTP Gateway")
    if profile:
        target_email = profile.get("email") or "dungavathpradeepnaik123@gmail.com"
        target_name = profile.get("full_name") or "Pradeep Naik"
        
        st.markdown(f"**Target Candidate:** `{target_name}`")
        st.markdown(f"**Destination Inbox:** `<span style='color:#34d399;'>{target_email}</span>`", unsafe_allow_html=True)
        st.markdown(f"**Current Matched Roles in Queue:** `{len(st.session_state.get('jobs_data', []))}`")
        
        if st.button("🚀 Trigger Email Digest Now", use_container_width=True):
            current_jobs = st.session_state.get("jobs_data", [])
            if current_jobs:
                with st.spinner("Connecting to SMTP server and dispatching email digest..."):
                    success = send_email_alert(target_email, target_name, current_jobs)
                    if success:
                        st.success(f"✅ High-match job digest successfully sent to {target_email}!")
                    else:
                        st.error("❌ Failed to send email. Please check your SMTP App Password configuration.")
            else:
                st.warning("⚠️ No jobs in queue! Please search jobs in the 'Neural Job Feed' tab first.")
    else:
        st.warning("⚠️ Please upload your resume in the sidebar to configure the candidate profile and email.")

# --- Bottom Footer (2 Lines) ---
st.markdown("""
<div class='footer-container'>
    ⚡ <b>JobNexus AI Engine Architected & Engineered by</b><br>
    <b style='color: #38bdf8; font-size: 1.05rem;'>Dongavath Pradeep</b>
</div>
""", unsafe_allow_html=True)
