import os
import json
import sqlite3
import streamlit as st

from resume_parser import parse_resume
from job_search import search_jobs
from email_notifier import send_email_alert

# --- Streamlit Layout Configuration ---
st.set_page_config(
    page_title="JobNexus - IT Career & Skill Gap Engine",
    page_icon="💼",
    layout="wide"
)

# --- UI Styling (Dark Aurora Gradient + Glassmorphism + Hide Deploy Badge) ---
custom_ui_style = """
    <style>
    /* Hide Deploy Badge / Viewer Avatar */
    [data-testid="stStatusWidget"],
    .viewerBadge_container__r5tak,
    div[class*="viewerBadge"] {
        display: none !important;
    }

    /* Modern Dark Aurora Background */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%) !important;
        color: #f8fafc;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* Glassmorphism Containers for Job Cards */
    [data-testid="stVerticalBlock"] > div[data-testid="stBlock"] {
        background: rgba(30, 41, 59, 0.7) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        backdrop-filter: blur(10px) !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3) !important;
    }

    /* Sidebar Customization */
    section[data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.95) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    }

    /* Interactive Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3) !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 18px rgba(99, 102, 241, 0.5) !important;
    }

    /* Matched & Missing Skill Badges */
    .badge-matched {
        background: rgba(16, 185, 129, 0.2);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.4);
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.85rem;
        margin-right: 6px;
        display: inline-block;
        margin-bottom: 6px;
        font-weight: 500;
    }
    
    .badge-missing {
        background: rgba(239, 68, 68, 0.2);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.4);
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.85rem;
        margin-right: 6px;
        display: inline-block;
        margin-bottom: 6px;
        font-weight: 500;
    }
    </style>
"""
st.markdown(custom_ui_style, unsafe_allow_html=True)

# --- Database Setup ---
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

# --- Match & Skill Gap Engine ---
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

# Initialize DB
init_db()

# --- JobNexus Visual Header Banner ---
st.markdown("""
<div style="text-align: left; padding: 10px 0px 5px 0px;">
    <svg width="340" height="65" viewBox="0 0 340 65" fill="none" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="auroraGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stop-color="#38bdf8" />
                <stop offset="50%" stop-color="#818cf8" />
                <stop offset="100%" stop-color="#c084fc" />
            </linearGradient>
            <linearGradient id="iconGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#38bdf8" />
                <stop offset="100%" stop-color="#6366f1" />
            </linearGradient>
            <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="6" result="blur" />
                <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
        </defs>

        <!-- Modern Nexus Node Icon -->
        <g transform="translate(5, 12)">
            <circle cx="18" cy="18" r="16" stroke="url(#iconGrad)" stroke-width="2.5" fill="rgba(99,102,241,0.15)"/>
            <circle cx="18" cy="18" r="5" fill="url(#iconGrad)"/>
            <line x1="18" y1="2" x2="18" y2="8" stroke="#38bdf8" stroke-width="2" stroke-linecap="round"/>
            <line x1="18" y1="28" x2="18" y2="34" stroke="#818cf8" stroke-width="2" stroke-linecap="round"/>
            <line x1="2" y1="18" x2="8" y2="18" stroke="#38bdf8" stroke-width="2" stroke-linecap="round"/>
            <line x1="28" y1="18" x2="34" y2="18" stroke="#c084fc" stroke-width="2" stroke-linecap="round"/>
        </g>

        <!-- Brand Text with Aurora Gradient -->
        <text x="55" y="39" font-family="'Segoe UI', 'Inter', -apple-system, sans-serif" font-weight="900" font-size="36" fill="url(#auroraGrad)" filter="url(#glow)">Job</text>
        <text x="120" y="39" font-family="'Segoe UI', 'Inter', -apple-system, sans-serif" font-weight="400" font-size="36" fill="#f8fafc" letter-spacing="1">Nexus</text>
    </svg>
</div>
""", unsafe_allow_html=True)

st.caption("Discover Tech Roles, Debug Your Skill Gaps, and Land Your Next Opportunity")

# --- Sidebar: Resume Upload & Candidate Info ---
with st.sidebar:
    st.header("📄 Candidate Profile")
    uploaded_file = st.file_uploader("Upload your PDF Resume", type=["pdf"])
    
    if uploaded_file is not None:
        if st.button("Ingest Resume", use_container_width=True):
            with st.spinner("Parsing resume and analyzing profile..."):
                temp_path = f"temp_{uploaded_file.name}"
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                try:
                    parsed_data = parse_resume(temp_path)
                    store_candidate_profile(parsed_data)
                    st.success("Resume parsed and saved successfully!")
                finally:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
    
    st.markdown("---")
    if st.button("Load Stored Profile", use_container_width=True):
        profile = get_candidate_profile()
        if profile:
            st.write(f"**Name:** {profile.get('full_name')}")
            st.write(f"**Email:** {profile.get('email')}")
            st.write(f"**Phone:** {profile.get('phone')}")
            st.write("**Extracted Skills:**")
            skills = profile.get("skills", [])
            st.info(", ".join(skills) if skills else "No skills parsed yet.")
        else:
            st.warning("No candidate profile found. Please upload a resume first.")

# --- Main Screen: Job Match & Gap Engine ---
st.subheader("🔍 Job Match Engine")

col1, col2, col3, col4 = st.columns([2, 1.5, 1.5, 1])

with col1:
    role_query = st.text_input("Target Job Role", value="Python Developer", placeholder="e.g. Python Developer, Data Scientist")
with col2:
    exp_level = st.selectbox(
        "Experience Level",
        ["Fresher / Entry Level", "Experienced (1-3 yrs)", "Senior (4+ yrs)", "All Levels"]
    )
with col3:
    location_query = st.selectbox(
        "Preferred Location",
        ["Hyderabad", "Bangalore", "Pune", "Chennai", "Mumbai", "Noida", "Gurgaon", "Remote"]
    )
with col4:
    st.write("")
    st.write("")
    search_btn = st.button("Search Jobs", use_container_width=True, type="primary")

if search_btn and role_query:
    profile = get_candidate_profile()
    if not profile:
        st.error("Candidate profile not found. Please upload your resume from the left sidebar first.")
    else:
        search_term = role_query
        if exp_level == "Fresher / Entry Level":
            search_term = f"{role_query} fresher"
        elif exp_level == "Senior (4+ yrs)":
            search_term = f"Senior {role_query}"

        with st.spinner(f"Fetching '{search_term}' jobs in '{location_query}'..."):
            raw_jobs = search_jobs(role=search_term, location=location_query)
            results = score_jobs(profile.get("skills", []), raw_jobs)
            
            st.write(f"Found **{len(results)}** active opportunities for **{exp_level}** in **{location_query}**:")
            
            for job in results:
                with st.container(border=True):
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.markdown(f"### {job.get('title')}")
                        st.markdown(f"**Company:** {job.get('company')} | **Location:** {job.get('location')} | **Level:** {exp_level}")
                        
                        # Matched Skills Tag Badges
                        matched = job.get("matched_skills", [])
                        if matched:
                            matched_html = "".join([f"<span class='badge-matched'>✓ {s}</span>" for s in matched])
                            st.markdown(f"**Matched Skills:** {matched_html}", unsafe_allow_html=True)
                        else:
                            st.write("**Matched Skills:** None detected")
                        
                        # Missing Skills / Skill Gaps Tag Badges
                        missing = job.get("missing_skills", [])
                        if missing:
                            missing_html = "".join([f"<span class='badge-missing'>✗ {s}</span>" for s in missing])
                            st.markdown(f"**Missing Skills (Skill Gap to Learn):** {missing_html}", unsafe_allow_html=True)
                        else:
                            st.markdown("**Missing Skills:** <span class='badge-matched'>None! You cover all core skills.</span>", unsafe_allow_html=True)
                        
                        st.write("")
                        if job.get("url"):
                            st.markdown(f"[🚀 **Apply on Portal**]({job.get('url')})")
                    
                    with c2:
                        score = int(job.get("match_score", 0))
                        st.metric(label="Match Score", value=f"{score}%")
                        st.progress(score / 100)

st.markdown("---")
# --- Email Alerts Section ---
st.subheader("📬 Automated Location Alerts")
alert_col1, alert_col2 = st.columns([3, 1])
with alert_col1:
    threshold = st.slider("Minimum Match Score Threshold (%)", min_value=50, max_value=100, value=75)
with alert_col2:
    st.write("")
    st.write("")
    if st.button("Trigger Email Digest", use_container_width=True):
        profile = get_candidate_profile()
        if not profile:
            st.error("Please upload a resume first.")
        else:
            search_term = f"{role_query} fresher" if exp_level == "Fresher / Entry Level" else role_query
            with st.spinner(f"Dispatching SMTP digest for {location_query}..."):
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
                        st.success(f"Email sent successfully to {profile.get('email')}!")
                    else:
                        st.error("Failed to send email. Please check your credentials.")
                else:
                    st.warning("No jobs matched the score threshold.")
