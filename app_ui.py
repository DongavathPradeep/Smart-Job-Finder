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

# --- High-Contrast UI Styling with Modern IT Campus Infrastructure ---
custom_ui_style = """
    <style>
    header[data-testid="stHeader"] { background: transparent !important; }
    [data-testid="stStatusWidget"], div[class*="viewerBadge"] { display: none !important; }

    /* Modern IT Enterprise Campus & Infrastructure Background */
    .stApp {
        background: linear-gradient(rgba(10, 15, 30, 0.88), rgba(15, 23, 42, 0.93)), 
                    url('https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?q=80&w=2070&auto=format&fit=crop') no-repeat center center fixed !important;
        background-size: cover !important;
        color: #f1f5f9 !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    }

    /* Streamlit Tabs Cyan Accent */
    button[data-baseweb="tab"] {
        background-color: rgba(30, 41, 59, 0.7) !important;
        border: 1px solid #334155 !important;
        border-radius: 8px 8px 0 0 !important;
        padding: 8px 16px !important;
        margin-right: 6px !important;
    }
    button[data-baseweb="tab"] div p, button[data-baseweb="tab"] div span {
        color: #94a3b8 !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: #1e293b !important;
        border-bottom: 3px solid #38bdf8 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] div p, 
    button[data-baseweb="tab"][aria-selected="true"] div span {
        color: #38bdf8 !important;
        font-weight: 800 !important;
    }

    /* Input & Select Box Styling */
    .stTextInput input, .stSelectbox > div > div {
        background-color: #1e293b !important;
        color: #ffffff !important;
        border: 1px solid #38bdf8 !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
    }

    label, .stTextInput label, .stSelectbox label, .stSlider label {
        color: #38bdf8 !important;
        font-weight: 700 !important;
        font-size: 0.92rem !important;
    }

    /* Primary Action Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
        color: #ffffff !important;
        border: 1px solid #3b82f6 !important;
        border-radius: 6px !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.3) !important;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: rgba(11, 17, 32, 0.98) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(10px) !important;
    }

    /* Metric Cards */
    [data-testid="stMetric"] {
        background: rgba(30, 41, 59, 0.85) !important;
        border: 1px solid rgba(56, 189, 248, 0.3) !important;
        border-radius: 8px !important;
        padding: 12px !important;
    }

    /* Job Glassmorphism Cards */
    .job-card {
        background-color: rgba(30, 41, 59, 0.88);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 8px;
        padding: 18px;
        margin-bottom: 12px;
        backdrop-filter: blur(8px);
    }

    /* Badges */
    .tag-match {
        background-color: #064e3b;
        color: #34d399;
        border: 1px solid #059669;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.82rem;
        margin-right: 6px;
        display: inline-block;
        font-weight: 600;
    }
    .tag-gap {
        background-color: #7f1d1d;
        color: #f87171;
        border: 1px solid #dc2626;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.82rem;
        margin-right: 6px;
        display: inline-block;
        font-weight: 600;
    }
    .tag-salary {
        background-color: rgba(245, 158, 11, 0.2);
        color: #fbbf24;
        border: 1px solid #d97706;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.82rem;
        margin-right: 6px;
        display: inline-block;
        font-weight: 700;
    }

    /* Steps Guide Box */
    .guide-card {
        background: rgba(15, 23, 42, 0.75);
        border: 1px dashed rgba(56, 189, 248, 0.4);
        border-radius: 8px;
        padding: 14px;
        margin-bottom: 15px;
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

def estimate_comp(exp_tier: str) -> str:
    if "Fresher" in exp_tier:
        return "₹4.0L – ₹6.5L PA (Est.)"
    elif "1-3" in exp_tier:
        return "₹7.0L – ₹12.5L PA (Est.)"
    else:
        return "₹14.0L – ₹24.0L+ PA (Est.)"

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
<div style='display: flex; justify-content: space-between; align-items: center; padding-bottom: 12px; border-bottom: 1px solid #334155;'>
    <div>
        <h2 style='margin: 0; color: #f8fafc; font-size: 1.6rem; font-weight: 800;'>⚡ JobNexus Console</h2>
        <p style='margin: 2px 0 0 0; color: #94a3b8; font-size: 0.9rem;'>Automated Skill Gap Analysis & Opportunity Orchestrator</p>
    </div>
    <div style='display: flex; gap: 8px;'>
        <span style='background: #1e293b; border: 1px solid #38bdf8; color: #38bdf8; font-family: monospace; font-size: 0.8rem; padding: 4px 12px; border-radius: 4px; font-weight: 600;'>INFRASTRUCTURE ACTIVE</span>
        <span style='background: #1e293b; border: 1px solid #34d399; color: #34d399; font-family: monospace; font-size: 0.8rem; padding: 4px 12px; border-radius: 4px; font-weight: 600;'>SQLITE PROD</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.write("")

# --- Sidebar: Profile & Extraction Engine ---
with st.sidebar:
    st.markdown("<h3 style='color: #38bdf8; margin-bottom: 8px; font-weight: 700;'>📄 Candidate Profile</h3>", unsafe_allow_html=True)
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
                        
    st.markdown("<hr style='border: 0.5px solid #334155;'>", unsafe_allow_html=True)
    profile = get_candidate_profile()
    if profile:
        skills = profile.get("skills", [])
        ats_score = min(95, max(50, len(skills) * 12)) if skills else 30
        st.metric(label="ATS Readiness Index", value=f"{ats_score}/100")
        st.progress(ats_score / 100)
        
        st.markdown(f"**Name:** `{profile.get('full_name', 'N/A')}`")
        st.markdown(f"**Email:** `{profile.get('email', 'N/A')}`")
        st.markdown("**Identified Skills:**")
        if skills:
            tags = "".join([f"<span class='tag-match' style='margin-bottom: 4px;'>{s}</span>" for s in skills])
            st.markdown(tags, unsafe_allow_html=True)
        else:
            st.caption("No skills extracted.")
    else:
        st.info("Upload your resume to begin analyzing.")

# --- Master Console Tabs ---
tab_feed, tab_analytics, tab_roadmap, tab_tracker, tab_alerts = st.tabs([
    "🎯 Opportunity Feed", 
    "📊 Skill Gap Analytics",
    "🗺️ 7-Day Bridge Roadmap",
    "📋 Application Tracker", 
    "📬 Automation & SMTP"
])

# Initialize session states
if "jobs_data" not in st.session_state:
    st.session_state["jobs_data"] = []
if "role_input" not in st.session_state:
    st.session_state["role_input"] = "Python Developer"

with tab_feed:
    # Quick Suggested Role Chips
    st.caption("⚡ Quick Roles:")
    chip_col1, chip_col2, chip_col3, chip_col4 = st.columns(4)
    if chip_col1.button("🐍 Python Developer", use_container_width=True):
        st.session_state["role_input"] = "Python Developer"
        st.rerun()
    if chip_col2.button("📊 Data Engineer", use_container_width=True):
        st.session_state["role_input"] = "Data Engineer"
        st.rerun()
    if chip_col3.button("🌐 Full Stack Engineer", use_container_width=True):
        st.session_state["role_input"] = "Full Stack Engineer"
        st.rerun()
    if chip_col4.button("☁️ DevOps / Cloud", use_container_width=True):
        st.session_state["role_input"] = "DevOps Engineer"
        st.rerun()

    col1, col2, col3, col4 = st.columns([2, 1.2, 1.2, 0.8])
    with col1:
        role_query = st.text_input("Target Stack / Role", value=st.session_state["role_input"])
    with col2:
        exp_level = st.selectbox("Experience Tier", ["Fresher / Entry Level", "Experienced (1-3 yrs)", "Senior (4+ yrs)", "All"])
    with col3:
        location_query = st.selectbox("Hub Location", ["Hyderabad", "Bangalore", "Pune", "Chennai", "Mumbai", "Remote"])
    with col4:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        search_btn = st.button("Run Query", use_container_width=True)

    if search_btn and role_query:
        if not profile:
            st.error("Please upload a candidate resume from the left sidebar first.")
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
        
        df_export = pd.DataFrame(results)[["title", "company", "location", "match_score", "url"]]
        st.download_button(
            label="📥 Export Opportunities as CSV",
            data=df_export.to_csv(index=False),
            file_name="jobnexus_opportunities.csv",
            mime="text/csv"
        )
        st.write("")

        salary_estimate = estimate_comp(exp_level)

        for idx, job in enumerate(results):
            matched = job.get("matched_skills", [])
            missing = job.get("missing_skills", [])
            matched_html = "".join([f"<span class='tag-match'>✓ {s}</span>" for s in matched]) if matched else "<span style='color: #94a3b8;'>None detected</span>"
            missing_html = "".join([f"<span class='tag-gap'>✗ {s}</span>" for s in missing]) if missing else "<span style='color: #34d399;'>100% Core Alignment</span>"
            
            job_key = f"{job.get('title')}--{job.get('company')}"
            current_status = statuses.get(job_key, "Not Applied")

            st.markdown(f"""
            <div class='job-card'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <h4 style='margin: 0; color: #38bdf8;'>{job.get('title')}</h4>
                    <span style='font-size: 1.15rem; font-weight: 800; color: #34d399;'>{job.get('match_score')}% Match</span>
                </div>
                <p style='margin: 6px 0 10px 0; color: #cbd5e1; font-size: 0.88rem;'>
                    <b>{job.get('company')}</b> • {job.get('location')} • <span class='tag-salary'>{salary_estimate}</span>
                </p>
                <div style='margin-bottom: 6px;'>
                    <span style='color: #94a3b8; font-size: 0.82rem; font-weight: 600;'>Matched: </span>{matched_html}
                </div>
                <div style='margin-bottom: 12px;'>
                    <span style='color: #94a3b8; font-size: 0.82rem; font-weight: 600;'>Skill Gaps: </span>{missing_html}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            card_c1, card_c2, card_c3, card_c4 = st.columns([1.5, 1.2, 1.2, 1])
            with card_c1:
                if job.get("url"):
                    st.markdown(f"[🚀 **Apply on Portal**]({job.get('url')})")
            with card_c2:
                with st.expander("📝 Application Pitch"):
                    pitch_text = f"Hi Hiring Team at {job.get('company')},\n\nI am applying for the {job.get('title')} role. With my background in {', '.join(matched) if matched else 'core software engineering'}, I can contribute immediately to your development workflows.\n\nBest regards,\n{profile.get('full_name')}"
                    st.text_area("Cold Application Note", value=pitch_text, height=120, key=f"pitch_{idx}")
            with card_c3:
                with st.expander("🎯 Mock Interview Qs"):
                    q_skills = ", ".join(matched[:2] + missing[:2])
                    st.markdown(f"""
                    **Technical Questions for {job.get('title')}:**
                    1. How do you handle concurrency & performance optimization in your stack?
                    2. Explain your experience working with `{q_skills or 'Python/SQL'}` in production.
                    3. How do you design scalable REST APIs and secure endpoints?
                    """)
            with card_c4:
                new_status = st.selectbox(
                    "Track Status", 
                    ["Not Applied", "Applied", "Interviewing", "Saved"],
                    index=["Not Applied", "Applied", "Interviewing", "Saved"].index(current_status),
                    key=f"status_{idx}"
                )
                if new_status != current_status:
                    update_job_status(job.get("title"), job.get("company"), new_status)
                    st.rerun()
    else:
        st.markdown("""
        <div class='guide-card'>
            <h4 style='color: #38bdf8; margin:0 0 6px 0;'>💡 How to Get Started:</h4>
            <ol style='color: #94a3b8; margin: 0; padding-left: 20px; font-size: 0.9rem;'>
                <li>Upload your Resume (PDF) in the left sidebar and click <b>Parse & Ingest Profile</b>.</li>
                <li>Pick a suggested Quick Role chip or enter your target role above.</li>
                <li>Click <b>Run Query</b> to discover live matching roles, skill gap analytics, and interview questions.</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)

with tab_analytics:
    st.markdown("<h3 style='color:#38bdf8; font-weight:700;'>📊 Market Demand vs Profile Gap Intelligence</h3>", unsafe_allow_html=True)
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

with tab_roadmap:
    st.markdown("<h3 style='color:#38bdf8; font-weight:700;'>🗺️ 7-Day Targeted Upskilling Bridge</h3>", unsafe_allow_html=True)
    st.caption("Structured plan to close top skill gaps identified in your search results.")
    
    if results:
        all_missing = list(set([s for j in results for s in j.get("missing_skills", [])]))[:3]
        if all_missing:
            st.markdown(f"**Priority Focus Areas:** `{'` • `'.join(all_missing)}`")
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"""
                * **Day 1-2: Core Foundations & Docs**
                  Master architecture, syntax, and CLI workflows for `{all_missing[0] if len(all_missing)>0 else 'Advanced Python'}`.
                * **Day 3-4: Hands-on Mini Module**
                  Implement an API endpoint or Docker container applying `{all_missing[1] if len(all_missing)>1 else 'REST APIs'}`.
                """)
            with col_b:
                st.markdown(f"""
                * **Day 5-6: Integration & Project Patch**
                  Add `{all_missing[2] if len(all_missing)>2 else 'Unit Testing & CI/CD'}` to your existing GitHub repo.
                * **Day 7: Resume Keyword Optimization & Mock Re-test**
                  Update resume with project metrics and re-score on JobNexus.
                """)
        else:
            st.success("You already possess all primary core skills for these opportunities!")
    else:
        st.info("Execute a job query to generate your personalized 7-Day Skill Roadmap.")

with tab_tracker:
    st.markdown("<h3 style='color:#38bdf8; font-weight:700;'>📋 Application Status Tracker (SQLite)</h3>", unsafe_allow_html=True)
    conn = sqlite3.connect(DB_PATH)
    app_df = pd.read_sql("SELECT job_title AS 'Role', company AS 'Company', status AS 'Current Status', updated_at AS 'Last Updated' FROM applications ORDER BY updated_at DESC", conn)
    conn.close()
    
    if not app_df.empty:
        st.dataframe(app_df, use_container_width=True)
    else:
        st.info("No applications tracked yet. Update statuses in the 'Opportunity Feed' to track them here.")

with tab_alerts:
    st.markdown("<h3 style='color:#38bdf8; font-weight:700;'>📬 Automated SMTP Dispatch</h3>", unsafe_allow_html=True)
    st.caption("Send high-priority matches directly to your inbox.")
    
    threshold = st.slider("Score Threshold for Alerts (%)", 50, 100, 75)
    
    if st.button("Trigger Email Digest", use_container_width=True):
        profile = get_candidate_profile()
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
<div style='margin-top: 50px; padding: 16px 0; border-top: 1px solid #334155; display: flex; justify-content: space-between; font-size: 0.8rem; color: #94a3b8;'>
    <div>Stack: Python 3.11 • Streamlit • SQLite3 • Pandas</div>
    <div>Engineered by <span style='color: #38bdf8; font-weight: 700;'>D. Pradeep Naik</span></div>
</div>
""", unsafe_allow_html=True)
