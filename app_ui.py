import os
import json
import sqlite3
import streamlit as st

from resume_parser import parse_resume
from job_search import search_jobs
from email_notifier import send_email_alert

# --- Streamlit Layout Configuration ---
st.set_page_config(
    page_title="JobNexus | Developer Career Intelligence",
    page_icon="💼",
    layout="wide"
)

# --- Professional Developer Theme (No AI-like Neon Glow) ---
custom_ui_style = """
    <style>
    header[data-testid="stHeader"] { background: transparent !important; }
    [data-testid="stStatusWidget"], div[class*="viewerBadge"] { display: none !important; }

    /* Clean Dark Developer Theme */
    .stApp {
        background-color: #0d1117 !important;
        color: #c9d1d9 !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif !important;
    }

    /* Input Fields */
    .stTextInput input, .stSelectbox > div > div {
        background-color: #161b22 !important;
        color: #f0f6fc !important;
        border: 1px solid #30363d !important;
        border-radius: 6px !important;
    }

    /* Action Buttons (Solid GitHub-Style Theme) */
    .stButton > button {
        background-color: #238636 !important;
        color: #ffffff !important;
        border: 1px solid rgba(240, 246, 252, 0.1) !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
    }
    .stButton > button:hover {
        background-color: #2ea043 !important;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #010409 !important;
        border-right: 1px solid #21262d !important;
    }

    /* Cards */
    .job-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 6px;
        padding: 16px;
        margin-bottom: 12px;
    }

    /* Tags */
    .tag-match {
        background-color: rgba(46, 160, 67, 0.15);
        color: #3fb950;
        border: 1px solid rgba(46, 160, 67, 0.4);
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.78rem;
        margin-right: 5px;
        display: inline-block;
    }
    .tag-gap {
        background-color: rgba(248, 81, 73, 0.15);
        color: #f85149;
        border: 1px solid rgba(248, 81, 73, 0.4);
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.78rem;
        margin-right: 5px;
        display: inline-block;
    }
    </style>
"""
st.markdown(custom_ui_style, unsafe_allow_html=True)

# --- Database Layer ---
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

# --- Scoring Engine ---
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

# --- Top Navigation Header (Developer Style) ---
st.markdown("""
<div style='display: flex; justify-content: space-between; align-items: center; padding-bottom: 12px; border-bottom: 1px solid #21262d;'>
    <div>
        <h2 style='margin: 0; color: #f0f6fc; font-weight: 600; font-size: 1.6rem;'>JobNexus Engine</h2>
        <p style='margin: 0; color: #8b949e; font-size: 0.85rem;'>Automated Skill Gap Scorer & Tech Role Aggregator</p>
    </div>
    <div style='text-align: right;'>
        <span style='background-color: #21262d; color: #58a6ff; font-family: monospace; font-size: 0.75rem; padding: 4px 8px; border-radius: 4px;'>v2.4.0-stable</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.write("")

# --- Sidebar: Profile & DB Controls ---
with st.sidebar:
    st.markdown("<h4 style='color: #f0f6fc;'>Candidate Profile</h4>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
    
    if uploaded_file is not None:
        if st.button("Parse & Ingest Resume", use_container_width=True):
            with st.spinner("Extracting profile text & skills..."):
                temp_path = f"temp_{uploaded_file.name}"
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                try:
                    parsed_data = parse_resume(temp_path)
                    store_candidate_profile(parsed_data)
                    st.success("Candidate record stored in SQLite.")
                finally:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
    
    st.markdown("<hr style='border: 0.5px solid #21262d;'>", unsafe_allow_html=True)
    profile = get_candidate_profile()
    if profile:
        st.markdown(f"**Name:** `{profile.get('full_name', 'N/A')}`")
        st.markdown(f"**Email:** `{profile.get('email', 'N/A')}`")
        st.markdown("**Parsed Skills:**")
        skills = profile.get("skills", [])
        if skills:
            tags = "".join([f"<span class='tag-match'>{s}</span>" for s in skills])
            st.markdown(tags, unsafe_allow_html=True)
        else:
            st.caption("No skills identified.")
    else:
        st.caption("No active candidate profile loaded.")

# --- Main Tabs Layout ---
tab1, tab2 = st.tabs(["Opportunity Feed", "Alerts & Automation"])

with tab1:
    c1, c2, c3, c4 = st.columns([2, 1.2, 1.2, 0.8])
    with c1:
        role_query = st.text_input("Role Title", value="Python Developer")
    with c2:
        exp_level = st.selectbox("Experience", ["Fresher / Entry Level", "1-3 Years", "4+ Years", "All"])
    with c3:
        location_query = st.selectbox("Location", ["Hyderabad", "Bangalore", "Pune", "Chennai", "Remote"])
    with c4:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        search_btn = st.button("Query Jobs", use_container_width=True)

    if search_btn and role_query:
        if not profile:
            st.warning("Upload a resume to calculate skill match scores.")
        else:
            search_term = f"{role_query} fresher" if exp_level == "Fresher / Entry Level" else role_query
            with st.spinner("Querying job feeds..."):
                raw_jobs = search_jobs(role=search_term, location=location_query)
                results = score_jobs(profile.get("skills", []), raw_jobs)
                
                m1, m2, m3 = st.columns(3)
                m1.metric("Opportunities Fetched", len(results))
                avg_score = round(sum([j.get("match_score", 0) for j in results]) / len(results), 1) if results else 0
                m2.metric("Average Stack Alignment", f"{avg_score}%")
                m3.metric("Target Location", location_query)
                
                st.write("")
                for job in results:
                    matched = job.get("matched_skills", [])
                    missing = job.get("missing_skills", [])
                    matched_html = "".join([f"<span class='tag-match'>+ {s}</span>" for s in matched]) if matched else "<span style='color: #8b949e;'>None</span>"
                    missing_html = "".join([f"<span class='tag-gap'>- {s}</span>" for s in missing]) if missing else "<span style='color: #3fb950;'>All target skills satisfied</span>"
                    
                    st.markdown(f"""
                    <div class='job-card'>
                        <div style='display: flex; justify-content: space-between; align-items: baseline;'>
                            <h4 style='margin: 0; color: #58a6ff;'>{job.get('title')}</h4>
                            <span style='font-weight: 700; color: #f0f6fc; font-size: 1.1rem;'>{job.get('match_score')}% Match</span>
                        </div>
                        <p style='margin: 4px 0 10px 0; color: #8b949e; font-size: 0.85rem;'>
                            <b>{job.get('company')}</b> • {job.get('location')} • Experience: {exp_level}
                        </p>
                        <div style='margin-bottom: 6px;'>
                            <span style='color: #8b949e; font-size: 0.8rem;'>Matched Skills: </span>{matched_html}
                        </div>
                        <div>
                            <span style='color: #8b949e; font-size: 0.8rem;'>Missing Skills: </span>{missing_html}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    if job.get("url"):
                        st.markdown(f"[Apply via Career Portal]({job.get('url')})")

with tab2:
    st.markdown("#### Automated SMTP Dispatch")
    st.caption("Configured for scheduled or trigger-based career digests.")
    
    threshold = st.slider("Score Threshold for Alerts (%)", 50, 100, 75)
    
    if st.button("Trigger Test Digest", type="secondary"):
        if not profile:
            st.error("Please load a candidate profile first.")
        else:
            with st.spinner("Dispatching summary email via SMTP..."):
                jobs = search_jobs(role=role_query, location=location_query)
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
                    st.info("No opportunities met the threshold.")

# --- Engineering Footer ---
st.markdown("""
<div style='margin-top: 40px; padding: 15px 0; border-top: 1px solid #21262d; display: flex; justify-content: space-between; font-size: 0.8rem; color: #8b949e;'>
    <div>Architecture: Python, Streamlit, SQLite3, BeautifulSoup4</div>
    <div>Developer: D. Pradeep Naik</div>
</div>
""", unsafe_allow_html=True)
