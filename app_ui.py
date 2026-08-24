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

st.set_page_config(page_title="JobNexus | AI Vector Career Intelligence", page_icon="⚡", layout="wide")
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
init_db()

st.markdown("""
<div style='display:flex; justify-content:space-between; align-items:center; padding-bottom:12px; border-bottom:1px solid #334155;'>
    <div>
        <h2 style='margin:0; color:#f8fafc; font-size:1.6rem;'>⚡ JobNexus Neural Console</h2>
        <p style='margin:0; color:#94a3b8; font-size:0.9rem;'>Vector Embeddings & Semantic Skill Gap Architecture</p>
    </div>
    <div style='display: flex; gap: 8px;'>
        <span style='background:#1e293b; border:1px solid #38bdf8; color:#38bdf8; font-family:monospace; padding:4px 10px; border-radius:4px; font-size: 0.8rem;'>EMBEDDINGS: all-MiniLM-L6-v2</span>
        <span style='background:#1e293b; border:1px solid #34d399; color:#34d399; font-family:monospace; padding:4px 10px; border-radius:4px; font-size: 0.8rem;'>SQLITE PROD</span>
    </div>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<h3 style='color:#38bdf8;'>📄 Candidate Ingestion</h3>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload PDF Resume", type=["pdf"])
    if uploaded_file and st.button("Parse & Generate Embeddings", use_container_width=True):
        temp_path = f"temp_{uploaded_file.name}"
        with open(temp_path, "wb") as f: f.write(uploaded_file.getbuffer())
        try:
            store_candidate_profile(parse_resume(temp_path))
            st.success("Candidate vectors stored & initialized.")
        finally:
            if os.path.exists(temp_path): os.remove(temp_path)
            
    st.markdown("<hr style='border:0.5px solid #334155;'>", unsafe_allow_html=True)
    profile = get_candidate_profile()
    if profile:
        skills = profile.get("skills", [])
        ats = min(95, max(50, len(skills) * 12)) if skills else 30
        st.metric("Neural ATS Alignment", f"{ats}/100")
        st.progress(ats / 100)
        st.markdown(f"**Candidate:** `{profile.get('full_name')}`\n\n**Contact:** `{profile.get('email')}`")
        st.markdown("".join([f"<span class='tag-match'>{s}</span>" for s in skills]), unsafe_allow_html=True)

tab_feed, tab_analytics, tab_roadmap, tab_tracker, tab_alerts = st.tabs([
    "🎯 Neural Job Feed", "📊 Gap Intelligence", "🗺️ 7-Day Bridge Roadmap", "📋 Application Tracker", "📬 Automation & SMTP"
])

if "jobs_data" not in st.session_state: st.session_state["jobs_data"] = []
if "role_input" not in st.session_state: st.session_state["role_input"] = "Python Developer"

with tab_feed:
    col1, col2, col3, col4 = st.columns([2, 1.2, 1.2, 0.8])
    role_query = col1.text_input("Target Role", value=st.session_state["role_input"])
    exp_level = col2.selectbox("Experience", ["Fresher / Entry Level", "1-3 yrs", "4+ yrs", "All"])
    location_query = col3.selectbox("Location", ["Hyderabad", "Bangalore", "Pune", "Chennai", "Remote"])
    
    if col4.button("Run Vector Match", use_container_width=True) and profile:
        with st.spinner("Computing cosine distance across live JD embeddings..."):
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
            matched = "".join([f"<span class='tag-match'>✓ {s}</span>" for s in job.get("matched_skills", [])])
            missing = "".join([f"<span class='tag-gap'>✗ {s}</span>" for s in job.get("missing_skills", [])])
            
            st.markdown(f"""
            <div class='job-card'>
                <div style='display:flex; justify-content:space-between;'>
                    <h4 style='color:#38bdf8; margin:0;'>{job.get('title')}</h4>
                    <span style='color:#34d399; font-weight:800;'>{job.get('semantic_score')}% Semantic Match</span>
                </div>
                <p style='color:#cbd5e1; font-size:0.88rem;'><b>{job.get('company')}</b> • {job.get('location')}</p>
                <div style='margin-bottom:6px;'><b>Direct Matches:</b> {matched or 'None detected'}</div>
                <div><b>Skill Gaps:</b> {missing or '<span style=\"color:#34d399;\">None</span>'}</div>
            </div>
            """, unsafe_allow_html=True)
            
            c1, c2 = st.columns([3, 1])
            if job.get("url"): c1.markdown(f"[🚀 **Apply via Portal**]({job.get('url')})")
            new_st = c2.selectbox("Status", ["Not Applied", "Applied", "Interviewing", "Saved"], 
                                  index=["Not Applied", "Applied", "Interviewing", "Saved"].index(statuses.get(f"{job.get('title')}--{job.get('company')}", "Not Applied")), 
                                  key=f"st_{idx}")
            if new_st != statuses.get(f"{job.get('title')}--{job.get('company')}", "Not Applied"):
                update_job_status(job.get("title"), job.get("company"), new_st)
                st.rerun()

with tab_analytics:
    if results:
        all_miss = [s for j in results for s in j.get("missing_skills", [])]
        if all_miss: 
            st.caption("Top Missing Market Skills by Vector Frequency")
            st.bar_chart(pd.Series(all_miss).value_counts().head(8))
        else: 
            st.success("High semantic vector alignment across all skills!")

with tab_roadmap:
    st.markdown("#### 🗺️ 7-Day Targeted Upskilling Bridge")
    st.write("Day 1-2: Vector Foundations | Day 3-4: Build API | Day 5-6: Containerization | Day 7: Resume Re-indexing")

with tab_tracker:
    conn = sqlite3.connect("candidate.db")
    st.dataframe(pd.read_sql("SELECT job_title AS 'Role', company AS 'Company', status AS 'Status' FROM applications", conn), use_container_width=True)
    conn.close()

with tab_alerts:
    if st.button("Trigger Email Digest", use_container_width=True) and profile:
        send_email_alert(profile.get("email"), profile.get("full_name"), results)
        st.success("Alert processed via SMTP.")