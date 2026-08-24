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

# --- Page Configuration ---
st.set_page_config(page_title="JobNexus | AI Vector Career Intelligence", page_icon="⚡", layout="wide")
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
init_db()

# --- Custom Styling: Vibrant Gradients & Clean UI ---
st.markdown("""
<style>
/* Gradient Header Title */
.gradient-title {
    background: linear-gradient(135deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 1.8rem;
    font-weight: 800;
    margin: 0;
}

/* Gradient Cards */
.gradient-card {
    background: linear-gradient(145deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.85));
    border: 1px solid rgba(56, 189, 248, 0.25);
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 15px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
    transition: transform 0.2s ease, border-color 0.2s ease;
}
.gradient-card:hover {
    border-color: #38bdf8;
    transform: translateY(-2px);
}

/* Gradient Match Score Badge */
.gradient-badge-match {
    background: linear-gradient(135deg, #059669, #10b981);
    color: #ffffff;
    font-weight: 800;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.85rem;
    box-shadow: 0 2px 10px rgba(16, 185, 129, 0.3);
}

/* Skill Tags */
.tag-match {
    background: linear-gradient(135deg, rgba(6, 78, 59, 0.6), rgba(6, 95, 70, 0.8));
    border: 1px solid #10b981;
    color: #34d399;
    padding: 3px 9px;
    border-radius: 6px;
    font-size: 0.78rem;
    font-weight: 600;
    margin-right: 4px;
    display: inline-block;
}
.tag-gap {
    background: linear-gradient(135deg, rgba(127, 29, 29, 0.6), rgba(153, 27, 27, 0.8));
    border: 1px solid #ef4444;
    color: #f87171;
    padding: 3px 9px;
    border-radius: 6px;
    font-size: 0.78rem;
    font-weight: 600;
    margin-right: 4px;
    display: inline-block;
}

/* Footer */
.footer-container {
    margin-top: 50px;
    padding: 20px;
    border-top: 1px solid #334155;
    text-align: center;
    color: #94a3b8;
    font-size: 0.95rem;
    line-height: 1.6;
}
</style>
""", unsafe_allow_html=True)

# --- Top Header Section (Without the 2 Boxes) ---
st.markdown("""
<div style='padding-bottom:14px; border-bottom:1px solid #334155; margin-bottom: 20px;'>
    <h2 class='gradient-title'>⚡ JobNexus Neural Console</h2>
    <p style='margin:0; color:#94a3b8; font-size:0.9rem;'>Vector Embeddings & Semantic Skill Gap Architecture</p>
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
            profile_data = parse_resume(temp_path)
            store_candidate_profile(profile_data)
            st.success("Candidate profile & vectors initialized!")
            st.rerun()
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
        
        st.markdown(f"**Candidate:** `{c_name}`")
        st.markdown(f"**Email:** <br><code style='color:#34d399;'>{c_email}</code>", unsafe_allow_html=True)
        st.markdown("<div style='margin-top:10px;'><b>Extracted Skills:</b></div>", unsafe_allow_html=True)
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

# --- Navigation Tabs ---
tab_feed, tab_analytics, tab_roadmap, tab_tracker, tab_alerts = st.tabs([
    "🎯 Resume-Matched Jobs", "📊 Gap Intelligence", "🗺️ 7-Day Bridge Roadmap", "📋 Application Tracker", "📬 Automation & SMTP"
])

if "jobs_data" not in st.session_state:
    st.session_state["jobs_data"] = []

# ========================================================
# 1. TAB: RESUME-MATCHED JOBS (Skill-Driven Matching)
# ========================================================
with tab_feed:
    candidate_skills = profile.get("skills", []) if profile else []
    
    # Default query automatically adapts to the top skills from the resume
    default_role = ", ".join(candidate_skills[:3]) if candidate_skills else "Python, Machine Learning, SQL"

    col1, col2, col3, col4 = st.columns([2.2, 1.1, 1.1, 0.9])
    role_query = col1.text_input(
        "Target Roles / Skill Set (Auto-loaded from Resume)", 
        value=default_role,
        help="Matches jobs directly according to the skills found in your uploaded resume"
    )
    
    exp_level = col2.selectbox("Experience", ["Fresher / Entry Level", "1-3 yrs", "4+ yrs", "All"])
    location_query = col3.selectbox("Location", ["Hyderabad", "Bangalore", "Pune", "Chennai", "Remote"])
    
    if col4.button("🚀 Fetch Matched Jobs", use_container_width=True):
        if not profile:
            st.warning("⚠️ Please upload your resume in the sidebar first!")
        else:
            with st.spinner("Analyzing resume skills & computing cosine distance across live jobs..."):
                raw = search_jobs(role=role_query, location=location_query)
                st.session_state["jobs_data"] = calculate_semantic_fit(profile, raw)

    # Auto-fetch on initial resume upload if empty
    if not st.session_state.get("jobs_data") and profile:
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
                <p style='color:#cbd5e1; font-size:0.88rem; margin: 4px 0 10px 0;'><b>{job.get('company')}</b> • {job.get('location')}</p>
                <div style='margin-bottom:6px;'><b>Direct Skill Matches:</b> {matched_html}</div>
                <div><b>Skill Gaps to Cover:</b> {missing_html}</div>
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
# 2. TAB: GAP INTELLIGENCE
# ========================================================
with tab_analytics:
    if results:
        all_miss = [s for j in results for s in j.get("missing_skills", [])]
        if all_miss: 
            st.caption("Top Missing Market Skills by Vector Frequency")
            st.bar_chart(pd.Series(all_miss).value_counts().head(8))
        else: 
            st.success("High semantic vector alignment across all skills!")
    else:
        st.info("Upload your resume and fetch jobs to view gap analytics.")

# ========================================================
# 3. TAB: ROADMAP
# ========================================================
with tab_roadmap:
    st.markdown("#### 🗺️ 7-Day Targeted Upskilling Bridge")
    st.write("Day 1-2: Core Foundations & Frameworks | Day 3-4: Build Vector Pipeline Project | Day 5-6: Integration & Deployment | Day 7: Re-index Profile")

# ========================================================
# 4. TAB: APPLICATION TRACKER
# ========================================================
with tab_tracker:
    conn = sqlite3.connect("candidate.db")
    df_track = pd.read_sql("SELECT job_title AS 'Role', company AS 'Company', status AS 'Status', updated_at AS 'Updated' FROM applications", conn)
    conn.close()
    if not df_track.empty:
        st.dataframe(df_track, use_container_width=True)
    else:
        st.info("No applications logged yet. Search jobs and mark status as 'Applied' or 'Saved'.")

# ========================================================
# 5. TAB: AUTOMATION & SMTP (Email Alerts)
# ========================================================
with tab_alerts:
    st.markdown("### 📬 Email Automation & SMTP Gateway")
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
                        st.error("❌ Failed to send email. Check your SMTP App Password configuration.")
            else:
                st.warning("⚠️ No jobs in queue! Fetch jobs in the first tab first.")
    else:
        st.warning("⚠️ Please upload your resume in the sidebar to configure the candidate profile.")

# --- Bottom Footer (2 Lines) ---
st.markdown("""
<div class='footer-container'>
    ⚡ <b>JobNexus AI Engine Architected & Engineered by</b><br>
    <b style='color: #38bdf8; font-size: 1.05rem;'>Dongavath Pradeep</b>
</div>
""", unsafe_allow_html=True)
