import os
import json
import sqlite3
import pandas as pd
import streamlit as st

from resume_parser import parse_resume
from job_search import search_jobs
from email_notifier import send_email_alert

# --- Streamlit Layout Configuration ---
st.set_page_config(
    page_title="JobNexus | Enterprise Tech Career Intelligence",
    page_icon="⚡",
    layout="wide"
)

# --- Clean Engineering UI Styling with IT Infrastructure Overlay ---
custom_ui_style = """
    <style>
    header[data-testid="stHeader"] { background: transparent !important; }
    [data-testid="stStatusWidget"], div[class*="viewerBadge"] { display: none !important; }

    /* IT Infrastructure Server/Data Center Background with Dark Overlay */
    .stApp {
        background: linear-gradient(rgba(11, 15, 25, 0.90), rgba(15, 23, 42, 0.94)), 
                    url('https://images.unsplash.com/photo-1558494949-ef010cbdcc31?q=80&w=2000&auto=format&fit=crop') no-repeat center center fixed !important;
        background-size: cover !important;
        color: #c9d1d9 !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    }

    /* Input & Select Box Styling */
    .stTextInput input, .stSelectbox > div > div {
        background-color: #111827 !important;
        color: #f3f4f6 !important;
        border: 1px solid #374151 !important;
        border-radius: 6px !important;
    }

    label, .stTextInput label, .stSelectbox label, .stSlider label {
        color: #38bdf8 !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
    }

    /* Primary Action Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
        color: #ffffff !important;
        border: 1px solid #3b82f6 !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: rgba(3, 7, 18, 0.95) !important;
        border-right: 1px solid #1f2937 !important;
        backdrop-filter: blur(8px) !important;
    }

    /* Metric Cards */
    [data-testid="stMetric"] {
        background: rgba(17, 24, 39, 0.85) !important;
        border: 1px solid #1f2937 !important;
        border-radius: 8px !important;
        padding: 12px !important;
        backdrop-filter: blur(6px) !important;
    }

    /* Job Glassmorphism Cards */
    .job-card {
        background-color: rgba(17, 24, 39, 0.88);
        border: 1px solid #1f2937;
        border-radius: 8px;
        padding: 18px;
        margin-bottom: 12px;
        backdrop-filter: blur(8px);
    }

    /* Badges */
    .tag-match {
        background-color: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.4);
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
        margin-right: 6px;
        display: inline-block;
    }
    .tag-gap {
        background-color: rgba(239, 68, 68, 0.15);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.4);
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
        margin-right: 6px;
        display: inline-block;
    }
    </style>
"""
st.markdown(custom_ui_style, unsafe_allow_html=True)

# --- SQLite Database Layer ---
DB_PATH = "candidate.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS candidate (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT,
            email TEXT,
            phone TEXT,
            skills TEXT,
            summary TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_title TEXT,
            company TEXT,
            status TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def store_candidate_profile(data: dict):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM candidate")
    skills_json = json.dumps(data.get("skills", []))
    cursor.execute("""
        INSERT INTO candidate (full_name, email, phone, skills, summary)
        VALUES (?, ?, ?, ?, ?)
    """, (
        data.get("full_name", "Anonymous Candidate"),
        data.get("email", ""),
        data.get("phone", ""),
        skills_json,
        data.get("summary", "")
    ))
    conn.commit()
    conn.close()

def get_candidate_profile() -> dict:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT full_name, email, phone, skills, summary FROM candidate ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    if not row:
        return {}
    return {
        "full_name": row[0],
        "email": row[1],
        "phone": row[2],
        "skills": json.loads(row[3]) if row[3] else [],
        "summary": row[4]
    }

def update_job_status(job_title: str, company: str, status: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM applications WHERE job_title = ? AND company = ?", (job_title, company))
    exists = cursor.fetchone()
    if exists:
        cursor.execute("UPDATE applications SET status = ? WHERE id = ?", (status, exists[0]))
    else:
        cursor.execute("INSERT INTO applications (job_title, company, status) VALUES (?, ?, ?)", (job_title, company, status))
    conn.commit()
    conn.close()

def get_job_statuses() -> dict:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT job_title, company, status FROM applications")
    rows = cursor.fetchall()
    conn.close()
    return {f"{r[0]}--{r[1]}": r[2] for r in rows}

# --- Match & Skill Engine ---
def score_jobs(candidate_skills: list, jobs: list) -> list:
    candidate_skills_lower = {s.lower().strip() for s in candidate_skills}
    tech_keywords = [
        "python", "django", "fastapi", "flask", "sql", "postgresql", "mysql", "mongodb",
        "docker", "kubernetes", "aws", "azure", "gcp", "git", "github", "rest api", "graphql",
        "pandas", "numpy", "react", "javascript", "typescript", "machine learning", "deep learning",
        "selenium", "html", "css", "tailwind", "linux", "ci/cd", "redis", "celery", "airflow"
    ]
    scored_jobs = []
    for job in jobs:
        title = job.get("title", "")
        desc = job.get("description", "")
        text = f"{title} {desc}".lower()
        
        matched = [s for s in candidate_skills if s.lower().strip() in text]
        required_in_job = [kw for kw in tech_keywords if kw in text]
        missing = [req for req in required_in_job if req not in candidate_skills_lower]
        
        missing = list(dict.fromkeys(missing))
        matched = list(dict.fromkeys(matched))
        
        if required_in_job:
            score = (len(matched) / (len(matched) + len(missing))) * 100 if (len(matched) + len(missing)) > 0 else 70.0
        else:
            score = 85.0 if matched else 45.0
            
        job_copy = dict(job)
        job_copy["match_score"] = min(100.0, round(score, 1))
        job_copy["matched_skills"] = matched
        job_copy["missing_skills"] = missing
        scored_jobs.append(job_copy)
        
    scored_jobs.sort(key=lambda x: x.get("match_score", 0), reverse=True)
    return scored_jobs

init_db()

# --- Top Console Navigation ---
st.markdown("""
<div style='display: flex; justify-content: space-between; align-items: center; padding-bottom: 12px; border-bottom: 1px solid #1f2937;'>
    <div>
        <h2 style='margin: 0; color: #f3f4f6; font-size: 1.5rem; font-weight: 700;'>⚡ JobNexus Console</h2>
        <p style='margin: 2px 0 0 0; color: #9ca3af; font-size: 0.85rem;'>Automated Skill Gap Analysis & Opportunity Orchestrator</p>
    </div>
    <div style='display: flex; gap: 8px;'>
        <span style='background: #111827; border: 1px solid #374151; color: #38bdf8; font-family: monospace; font-size: 0.75rem; padding: 4px 10px; border-radius: 4px;'>INFRASTRUCTURE ACTIVE</span>
        <span style='background: #111827; border: 1px solid #374151; color: #34d399; font-family: monospace; font-size: 0.75rem; padding: 4px 10px; border-radius: 4px;'>SQLITE PROD</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.write("")

# --- Sidebar: Profile & Extraction Engine ---
with st.sidebar:
    st.markdown("<h4 style='color: #f3f4f6; margin-bottom: 8px;'>Candidate Profile</h4>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload PDF Resume", type=["pdf"])
    
    if uploaded_file is not None:
        if st.button("Parse & Ingest Profile", use_container_width=True):
            with st.spinner("Extracting candidate metadata..."):
                temp_path = f"temp_{uploaded_file.name}"
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                try:
                    parsed_data = parse_resume(temp_path)
                    store_candidate_profile(parsed_data)
                    st.success("Resume ingested into SQLite schema.")
                finally:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                        
    st.markdown("<hr style='border: 0.5px solid #1f2937;'>", unsafe_allow_html=True)
    profile = get_candidate_profile()
    if profile:
        st.markdown(f"**Name:** `{profile.get('full_name', 'N/A')}`")
        st.markdown(f"**Email:** `{profile.get('email', 'N/A')}`")
        st.markdown("**Identified Skills:**")
        skills = profile.get("skills", [])
        if skills:
            tags = "".join([f"<span class='tag-match' style='margin-bottom: 4px;'>{s}</span>" for s in skills])
            st.markdown(tags, unsafe_allow_html=True)
        else:
            st.caption("No skills extracted.")
    else:
        st.info("Upload a resume to begin scoring.")

# --- Master Console Tabs ---
tab_feed, tab_analytics, tab_tracker, tab_alerts = st.tabs([
    "🎯 Opportunity Feed", 
    "📊 Skill Gap Analytics", 
    "📋 Application Tracker", 
    "📬 Automation & SMTP"
])

# Initialize session state for searched results
if "jobs_data" not in st.session_state:
    st.session_state["jobs_data"] = []

with tab_feed:
    col1, col2, col3, col4 = st.columns([2, 1.2, 1.2, 0.8])
    with col1:
        role_query = st.text_input("Target Stack / Role", value="Python Developer")
    with col2:
        exp_level = st.selectbox("Experience Tier", ["Fresher / Entry Level", "Experienced (1-3 yrs)", "Senior (4+ yrs)", "All"])
    with col3:
        location_query = st.selectbox("Hub Location", ["Hyderabad", "Bangalore", "Pune", "Chennai", "Mumbai", "Remote"])
    with col4:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        search_btn = st.button("Run Query", use_container_width=True)

    if search_btn and role_query:
        if not profile:
            st.error("Please upload a candidate resume first.")
        else:
            search_term = f"{role_query} fresher" if exp_level == "Fresher / Entry Level" else role_query
            with st.spinner("Fetching matching live roles..."):
                raw = search_jobs(role=search_term, location=location_query)
                st.session_state["jobs_data"] = score_jobs(profile.get("skills", []), raw)

    results = st.session_state.get("jobs_data", [])
    statuses = get_job_statuses()

    if results:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Roles Discovered", len(results))
        avg_score = round(sum([j.get("match_score", 0) for j in results]) / len(results), 1)
        m2.metric("Mean Stack Match", f"{avg_score}%")
        high_matches = len([j for j in results if j.get("match_score", 0) >= 75])
        m3.metric("High-Fit Roles (≥75%)", high_matches)
        m4.metric("Market Region", location_query)

        st.markdown("---")
        
        # Quick CSV Download
        df_export = pd.DataFrame(results)[["title", "company", "location", "match_score", "url"]]
        st.download_button(
            label="📥 Export Opportunities as CSV",
            data=df_export.to_csv(index=False),
            file_name="jobnexus_opportunities.csv",
            mime="text/csv"
        )
        st.write("")

        for idx, job in enumerate(results):
            matched = job.get("matched_skills", [])
            missing = job.get("missing_skills", [])
            matched_html = "".join([f"<span class='tag-match'>✓ {s}</span>" for s in matched]) if matched else "<span style='color: #6b7280;'>None detected</span>"
            missing_html = "".join([f"<span class='tag-gap'>✗ {s}</span>" for s in missing]) if missing else "<span style='color: #34d399;'>100% Core Alignment</span>"
            
            job_key = f"{job.get('title')}--{job.get('company')}"
            current_status = statuses.get(job_key, "Not Applied")

            st.markdown(f"""
            <div class='job-card'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <h4 style='margin: 0; color: #38bdf8;'>{job.get('title')}</h4>
                    <span style='font-size: 1.15rem; font-weight: 700; color: #34d399;'>{job.get('match_score')}% Match</span>
                </div>
                <p style='margin: 4px 0 10px 0; color: #9ca3af; font-size: 0.85rem;'>
                    <b>{job.get('company')}</b> • {job.get('location')} • Tier: {exp_level}
                </p>
                <div style='margin-bottom: 6px;'>
                    <span style='color: #9ca3af; font-size: 0.8rem; font-weight: 600;'>Matched: </span>{matched_html}
                </div>
                <div style='margin-bottom: 12px;'>
                    <span style='color: #9ca3af; font-size: 0.8rem; font-weight: 600;'>Skill Gaps: </span>{missing_html}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            card_c1, card_c2 = st.columns([3, 1])
            with card_c1:
                if job.get("url"):
                    st.markdown(f"[🚀 **Open Application Link**]({job.get('url')})")
            with card_c2:
                new_status = st.selectbox(
                    "Track Status", 
                    ["Not Applied", "Applied", "Interviewing", "Saved"],
                    index=["Not Applied", "Applied", "Interviewing", "Saved"].index(current_status),
                    key=f"status_{idx}"
                )
                if new_status != current_status:
                    update_job_status(job.get("title"), job.get("company"), new_status)
                    st.rerun()

with tab_analytics:
    st.markdown("#### Market Demand vs Profile Gap Intelligence")
    if results:
        all_missing = []
        for j in results:
            all_missing.extend(j.get("missing_skills", []))
        
        if all_missing:
            gap_counts = pd.Series(all_missing).value_counts().reset_index()
            gap_counts.columns = ["Skill", "Frequency"]
            gap_df = gap_counts.set_index("Skill")
            
            st.caption("Top Missing Skills in Market for Your Target Role (Demand Frequency)")
            st.bar_chart(gap_df.head(8))
        else:
            st.success("No skill gaps detected across the fetched job feeds!")
    else:
        st.info("Run a job query in the 'Opportunity Feed' tab to generate analytics.")

with tab_tracker:
    st.markdown("#### Application Status Tracker (SQLite)")
    conn = sqlite3.connect(DB_PATH)
    app_df = pd.read_sql("SELECT job_title AS 'Role', company AS 'Company', status AS 'Current Status', updated_at AS 'Last Updated' FROM applications ORDER BY updated_at DESC", conn)
    conn.close()
    
    if not app_df.empty:
        st.dataframe(app_df, use_container_width=True)
    else:
        st.info("No applications tracked yet. Update statuses in the 'Opportunity Feed' to track them here.")

with tab_alerts:
    st.markdown("#### Automated SMTP Dispatch")
    st.caption("Send high-priority matches directly to your inbox.")
    
    threshold = st.slider("Score Threshold for Alerts (%)", 50, 100, 75)
    
    if st.button("Trigger Email Digest", use_container_width=True):
        if not profile:
            st.error("Please load a candidate profile first.")
        else:
            search_term = f"{role_query} fresher" if exp_level == "Fresher / Entry Level" else role_query
            with st.spinner("Dispatching digest email..."):
                jobs = search_jobs(role=search_term, location=location_query)
                scored = score_jobs(profile.get("skills", []), jobs)
                qualified = [j for j in scored if j.get("match_score", 0) >= threshold]
                
                if qualified:
                    success = send_email_alert(
                        recipient_email=profile.get("email"),
                        candidate_name=profile.get("full_name"),
                        matched_jobs=qualified
                    )
                    if success:
                        st.success(f"Digest dispatched to {profile.get('email')}")
                    else:
                        st.error("Email service error. Check SMTP config.")
                else:
                    st.warning("No opportunities met the threshold.")

# --- Architecture Footer ---
st.markdown("""
<div style='margin-top: 50px; padding: 16px 0; border-top: 1px solid #1f2937; display: flex; justify-content: space-between; font-size: 0.8rem; color: #6b7280;'>
    <div>Stack: Python 3.11 • Streamlit • SQLite3 • Pandas</div>
    <div>Engineered by <span style='color: #38bdf8; font-weight: 600;'>D. Pradeep Naik</span></div>
</div>
""", unsafe_allow_html=True)
