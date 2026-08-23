import os
import json
import sqlite3
import streamlit as st

from resume_parser import parse_resume
from job_search import search_jobs
from email_notifier import send_email_alert

# --- Streamlit Layout Configuration ---
st.set_page_config(
    page_title="AI Job Application Agent",
    page_icon="💼",
    layout="wide"
)

# Hide Profile Badge CSS
hide_badge_style = """
    <style>
    [data-testid="stStatusWidget"],
    .viewerBadge_container__r5tak,
    div[class*="viewerBadge"] {
        display: none !important;
    }
    </style>
"""
st.markdown(hide_badge_style, unsafe_allow_html=True)

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

# --- Match Scoring Engine ---
def score_jobs(candidate_skills: list, jobs: list) -> list:
    candidate_skills_lower = {s.lower().strip() for s in candidate_skills}
    tech_keywords = [
        "python", "django", "fastapi", "flask", "sql", "postgresql", "mysql", 
        "docker", "aws", "git", "rest api", "pandas", "numpy", "react", "javascript", 
        "machine learning", "selenium", "html", "css"
    ]
    
    scored_jobs = []
    for job in jobs:
        title = job.get("title", "")
        desc = job.get("description", "")
        text = f"{title} {desc}".lower()
        
        matched = [s for s in candidate_skills if s.lower().strip() in text]
        required_in_job = [kw for kw in tech_keywords if kw in text]
        missing = [req for req in required_in_job if req not in candidate_skills_lower]
        
        if required_in_job:
            score = (len(matched) / len(required_in_job)) * 100
        else:
            score = 80.0 if matched else 40.0
            
        job_copy = dict(job)
        job_copy["match_score"] = min(100.0, round(score, 2))
        job_copy["matched_skills"] = matched
        job_copy["missing_skills"] = missing
        scored_jobs.append(job_copy)
        
    scored_jobs.sort(key=lambda x: x.get("match_score", 0), reverse=True)
    return scored_jobs

# Initialize DB
init_db()

st.title("💼 Autonomous AI Job Discovery & Apply Agent")
st.caption("Automate your job search, filter by experience level & location, analyze matches, and trigger alerts.")

# Sidebar: Resume Upload
with st.sidebar:
    st.header("📄 Candidate Profile")
    uploaded_file = st.file_uploader("Upload your PDF Resume", type=["pdf"])
    
    if uploaded_file is not None:
        if st.button("Ingest Resume", use_container_width=True):
            with st.spinner("Parsing resume and storing in database..."):
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
            st.info(", ".join(profile.get("skills", [])))
        else:
            st.warning("No candidate profile found. Please upload a resume first.")

# Main Screen: Search Engine with Experience Level
st.subheader("🔍 Job Match Engine")

col1, col2, col3, col4 = st.columns([2, 1.5, 1.5, 1])

with col1:
    role_query = st.text_input("Target Job Role", value="Python Developer", placeholder="e.g. Python Developer, Data Analyst")
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
        # Construct search query with experience level keyword
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
                        st.write("**Matched Skills:** " + ", ".join(job.get("matched_skills", [])))
                        if job.get("missing_skills"):
                            st.write("**Skill Gaps (To Learn):** " + ", ".join(job.get("missing_skills", [])))
                        if job.get("url"):
                            st.markdown(f"[Apply on Portal]({job.get('url')})")
                    with c2:
                        score = int(job.get("match_score", 0))
                        st.metric(label="Match Score", value=f"{score}%")
                        st.progress(score / 100)

st.markdown("---")
# Email Digest Section
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
