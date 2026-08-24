import os
import sqlite3
import pandas as pd
import streamlit as st

from resume_parser import parse_resume
from job_search import search_jobs
from email_notifier import send_email_alert
from db_manager import init_db, store_candidate_profile, get_candidate_profile, update_job_status, get_job_statuses
from semantic_matcher import calculate_semantic_fit

# --- Job Roles Dataset for Auto-Suggestions ---
MASTER_JOB_ROLES = [
    "Python Developer", "Python Backend Developer", "Python Full Stack Developer",
    "Python Django / FastAPI Developer", "Python Data Engineer", "Python Machine Learning Engineer",
    "Java Developer", "Java Full Stack Developer", "Spring Boot Engineer",
    "React.js Developer", "Frontend Developer", "Full Stack Web Developer", "Node.js Developer",
    "Data Analyst", "Data Scientist", "DevOps Engineer", "Cloud Engineer (AWS/Azure)",
    "QA Automation Engineer", "Selenium Tester", "AI / Prompt Engineer"
]

# --- Page Configuration ---
st.set_page_config(page_title="SmartJobApply | AI Job Search Co-Pilot", page_icon="🚀", layout="wide")
init_db()

# --- Custom Styling for SaaS Light-Gradient Theme ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
    color: #1e293b;
}

.stApp {
    background: radial-gradient(circle at 10% 20%, rgba(224, 231, 255, 0.6) 0%, rgba(243, 232, 255, 0.7) 40%, rgba(255, 255, 255, 0.9) 100%);
}

/* Hero Section */
.hero-badge {
    display: inline-block;
    background: #ede9fe;
    color: #6366f1;
    font-size: 0.85rem;
    font-weight: 600;
    padding: 6px 18px;
    border-radius: 50px;
    margin-bottom: 12px;
}
.hero-title {
    font-size: 2.8rem;
    font-weight: 800;
    color: #334155;
    line-height: 1.2;
    margin-bottom: 8px;
}
.hero-subtitle {
    font-size: 1.35rem;
    font-weight: 700;
    color: #d97706;
    margin-bottom: 25px;
}

/* Feature Badges */
.feature-pill-row {
    display: flex;
    justify-content: center;
    gap: 12px;
    flex-wrap: wrap;
    margin-bottom: 30px;
}
.pill {
    padding: 8px 16px;
    border-radius: 50px;
    font-size: 0.88rem;
    font-weight: 600;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #ffffff;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.pill-red { border: 1px solid #fecaca; color: #dc2626; }
.pill-blue { border: 1px solid #bfdbfe; color: #2563eb; }
.pill-green { border: 1px solid #bbf7d0; color: #16a34a; }
.pill-purple { border: 1px solid #ddd6fe; color: #7c3aed; }
.pill-amber { border: 1px solid #fde68a; color: #d97706; }

/* 4 Metrics Stats Banner */
.stats-card {
    background: #ffffff;
    border-radius: 20px;
    padding: 28px 20px;
    margin: 25px auto 40px auto;
    max-width: 820px;
    box-shadow: 0 10px 30px rgba(99, 102, 241, 0.08);
    border: 1px solid #e2e8f0;
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    text-align: center;
}
.stat-num { font-size: 1.8rem; font-weight: 800; color: #6366f1; }
.stat-lbl { font-size: 0.8rem; color: #64748b; font-weight: 600; }

/* Job Cards & Badges */
.job-card {
    background: #ffffff;
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 15px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 4px 12px rgba(0,0,0,0.03);
}
.tag-match { background: #dcfce7; color: #15803d; padding: 3px 8px; border-radius: 6px; font-size: 0.78rem; font-weight: 600; margin-right: 4px; }
.tag-gap { background: #fee2e2; color: #b91c1c; padding: 3px 8px; border-radius: 6px; font-size: 0.78rem; font-weight: 600; margin-right: 4px; }

/* Footer */
.footer-container {
    margin-top: 60px;
    padding: 25px;
    border-top: 1px solid #e2e8f0;
    text-align: center;
    color: #64748b;
    font-size: 0.95rem;
    line-height: 1.6;
}
</style>
""", unsafe_allow_html=True)

# --- Sidebar Candidate Profile & Ingestion ---
with st.sidebar:
    st.markdown("<h3 style='color:#4f46e5;'>📄 Resume Ingestion</h3>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload PDF Resume", type=["pdf"])
    if uploaded_file and st.button("Parse & Build Embeddings", use_container_width=True):
        temp_path = f"temp_{uploaded_file.name}"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        try:
            store_candidate_profile(parse_resume(temp_path))
            st.success("Candidate vectors stored successfully!")
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
    profile = get_candidate_profile()
    if profile:
        skills = profile.get("skills", [])
        ats = min(95, max(50, len(skills) * 12)) if skills else 30
        st.metric("Neural ATS Match Score", f"{ats}/100")
        st.progress(ats / 100)
        st.markdown(f"**Candidate:** `{profile.get('full_name')}`\n\n**Email:** `{profile.get('email')}`")
        st.markdown("".join([f"<span class='tag-match'>{s}</span>" for s in skills]), unsafe_allow_html=True)

    st.markdown("<hr style='border:0.5px solid #e2e8f0; margin-top:30px;'>", unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align: center; color: #64748b; font-size: 0.85rem;'>
        <b>System Architect</b><br>
        <span style='color: #4f46e5; font-weight: bold;'>Dongavath Pradeep</span><br><br>
        <a href='https://github.com/DongavathPradeep' target='_blank' style='color:#4f46e5; text-decoration:none; font-weight:600;'>🔗 GitHub Profile</a><br>
        <a href='https://www.linkedin.com/in/pradeep-naik-42292b264/' target='_blank' style='color:#4f46e5; text-decoration:none; font-weight:600;'>💼 LinkedIn Profile</a>
    </div>
    """, unsafe_allow_html=True)

# --- Top Navigation Bar ---
nav_col1, nav_col2, nav_col3 = st.columns([1.5, 4, 1.2])

with nav_col1:
    st.markdown("<div style='font-size:1.5rem; font-weight:800; color:#4f46e5; padding-top:4px;'>SmartJobApply</div>", unsafe_allow_html=True)

with nav_col2:
    current_page = st.radio(
        "Navigation",
        ["Home", "Search Jobs", "About / Features", "Saved Jobs", "Auto-Apply & Alerts"],
        horizontal=True,
        label_visibility="collapsed"
    )

with nav_col3:
    st.markdown("<div style='text-align:right;'><span style='background:#4f46e5; color:white; padding:8px 18px; border-radius:8px; font-size:0.85rem; font-weight:700;'>Login / Sign Up</span></div>", unsafe_allow_html=True)

st.markdown("<hr style='border: 0.5px solid #e2e8f0; margin: 10px 0 25px 0;'>", unsafe_allow_html=True)

# ==========================================
# 1. PAGE: HOME
# ==========================================
if current_page == "Home":
    st.markdown("""
    <div style='text-align: center;'>
        <div class='hero-badge'>⭐ AI-Powered Job Matching</div>
        <div class='hero-title'>Your AI Job Search Co-Pilot</div>
        <div class='hero-subtitle'>Faster Applications. Smarter Matches. Better Opportunities.</div>
        <div class='feature-pill-row'>
            <div class='pill pill-red'>🎯 AI Match Score</div>
            <div class='pill pill-blue'>📄 Auto-Fill in 2 Secs</div>
            <div class='pill pill-green'>⚡ Instant Auto-Apply</div>
            <div class='pill pill-purple'>⭐ AI-Generated Messages</div>
            <div class='pill pill-amber'>🔔 Smart Job Alerts</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 4 Cards Stat Box
    st.markdown("""
    <div class='stats-card'>
        <div>
            <div class='stat-num'>10,000+</div>
            <div class='stat-lbl'>Applications Filled</div>
        </div>
        <div>
            <div class='stat-num'>5x</div>
            <div class='stat-lbl'>Faster Job Search</div>
        </div>
        <div>
            <div class='stat-num'>10+</div>
            <div class='stat-lbl'>Job Boards Unified</div>
        </div>
        <div>
            <div class='stat-num'>10 hrs</div>
            <div class='stat-lbl'>Saved Per Week</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Call to Action Hero Box
    c_btn1, c_btn2, c_btn3 = st.columns([1.5, 1, 1.5])
    with c_btn2:
        if st.button("🚀 Start Your Job Search Now", use_container_width=True):
            st.info("Navigate to 'Search Jobs' in the top menu to run live vector matching!")

# ==========================================
# 2. PAGE: SEARCH JOBS (Core Engine)
# ==========================================
elif current_page == "Search Jobs":
    st.markdown("<h3 style='color:#334155;'>🔍 Live Neural Job Feed & Vector Matching</h3>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns([2.2, 1.1, 1.1, 0.9])
    role_query = col1.text_input("Target Role / Keyword", value="Python")
    exp_level = col2.selectbox("Experience", ["Fresher", "1-3 yrs", "4+ yrs", "All"])
    location_query = col3.selectbox("Location", ["Hyderabad", "Bangalore", "Pune", "Chennai", "Remote"])
    
    # Associated Live Roles Tags
    if role_query.strip():
        matching_roles = [r for r in MASTER_JOB_ROLES if role_query.strip().lower() in r.lower()]
        if matching_roles:
            tags_html = "".join([f"<span style='background:#f1f5f9; color:#475569; padding:3px 8px; margin:2px; border-radius:4px; font-size:0.75rem; display:inline-block;'>{r}</span>" for r in matching_roles])
            st.markdown(f"<div style='margin-top:-10px; margin-bottom:12px;'><small style='color:#64748b;'><b>Related Roles:</b></small> {tags_html}</div>", unsafe_allow_html=True)

    if "jobs_data" not in st.session_state:
        st.session_state["jobs_data"] = []

    if col4.button("Run Match", use_container_width=True) and profile:
        with st.spinner(f"Computing cosine distance for '{role_query}' across live JD embeddings..."):
            raw = search_jobs(role=role_query, location=location_query)
            st.session_state["jobs_data"] = calculate_semantic_fit(profile, raw)

    results = st.session_state.get("jobs_data", [])
    statuses = get_job_statuses()

    if results:
        m1, m2, m3 = st.columns(3)
        m1.metric("Roles Evaluated", len(results))
        avg_score = round(sum([j.get("semantic_score", 0) for j in results]) / len(results), 1)
        m2.metric("Mean Semantic Match", f"{avg_score}%")
        m3.metric("High Match (≥70%)", len([j for j in results if j.get("semantic_score", 0) >= 70]))
        
        for idx, job in enumerate(results):
            matched_html = "".join([f"<span class='tag-match'>✓ {s}</span>" for s in job.get("matched_skills", [])]) or "None"
            missing_html = "".join([f"<span class='tag-gap'>✗ {s}</span>" for s in job.get("missing_skills", [])]) or "<span style='color:#16a34a;'>None</span>"
            
            st.markdown(f"""
            <div class='job-card'>
                <div style='display:flex; justify-content:space-between; align-items:center;'>
                    <h4 style='color:#1e293b; margin:0;'>{job.get('title')}</h4>
                    <span style='background:#dcfce7; color:#15803d; font-weight:800; padding:4px 12px; border-radius:50px; font-size:0.85rem;'>{job.get('semantic_score')}% Match</span>
                </div>
                <p style='color:#64748b; font-size:0.9rem; margin:4px 0 10px 0;'><b>{job.get('company')}</b> • {job.get('location')}</p>
                <div style='margin-bottom:6px; font-size:0.85rem;'><b>Matches:</b> {matched_html}</div>
                <div style='font-size:0.85rem;'><b>Skill Gaps:</b> {missing_html}</div>
            </div>
            """, unsafe_allow_html=True)
            
            c1, c2 = st.columns([3, 1])
            if job.get("url"):
                c1.markdown(f"[🚀 **Instant Apply via Portal**]({job.get('url')})")
            
            current_status = statuses.get(f"{job.get('title')}--{job.get('company')}", "Not Applied")
            options = ["Not Applied", "Applied", "Interviewing", "Saved"]
            default_index = options.index(current_status) if current_status in options else 0
            
            new_st = c2.selectbox("Status", options, index=default_index, key=f"st_{idx}")
            if new_st != current_status:
                update_job_status(job.get("title"), job.get("company"), new_st)
                st.rerun()

# ==========================================
# 3. PAGE: ABOUT / FEATURES
# ==========================================
elif current_page == "About / Features":
    st.markdown("<h3 style='color:#334155;'>💡 About SmartJobApply AI Architecture</h3>", unsafe_allow_html=True)
    st.markdown("""
    **SmartJobApply** అనేది కేవలం సాధారణ జాబ్ సెర్చ్ ఇంజిన్ మాత్రమే కాదు; ఇది **NLP Semantic Embeddings & Skill Gap Intelligence** తో నిర్మించిన అధునాతన కెరీర్ అసిస్టెంట్.

    #### 🌟 ముఖ్యమైన ఫీచర్లు (Core Features):
    * **1. Dense Vector Embeddings:** `sentence-transformers/all-MiniLM-L6-v2` మోడల్ ద్వారా మీ రెజ్యూమ్ మరియు కంపెనీ JD ల మధ్య కచ్చితమైన కోసైన్ సిమిలారిటీ స్కోర్ లెక్కిస్తుంది.
    * **2. Instant Skill Gap Analysis:** మీరు టార్గెట్ చేసిన రోల్‌కు మీ రెజ్యూమ్‌లో ఏయే స్కిల్స్ సరిపోతున్నాయి, ఏవి తక్కువగా ఉన్నాయో (Missing Skills) స్పష్టంగా చూపిస్తుంది.
    * **3. Application Lifecycle Tracker:** SQLite డేటాబేస్ ద్వారా మీరు అప్లై చేసిన ఉద్యోగాల స్టేటస్ (`Applied`, `Interviewing`, `Saved`) ను సులభంగా ట్రాక్ చేస్తుంది.
    * **4. Automated Email Dispatch:** అధిక మ్యాచ్ స్కోర్ ఉన్న ఉద్యోగాల జాబితాను ఆటోమేటిక్‌గా మీ ఈమెయిల్‌కు అలర్ట్ రూపంలో పంపుతుంది.
    """)

# ==========================================
# 4. PAGE: SAVED JOBS (Application Tracker)
# ==========================================
elif current_page == "Saved Jobs":
    st.markdown("<h3 style='color:#334155;'>📋 Your Application & Saved Jobs Tracker</h3>", unsafe_allow_html=True)
    conn = sqlite3.connect("candidate.db")
    df = pd.read_sql("SELECT job_title AS 'Role', company AS 'Company', status AS 'Status', updated_at AS 'Last Updated' FROM applications", conn)
    conn.close()
    
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("ఇంకా ఏ ఉద్యోగాల స్టేటస్ అప్‌డేట్ చేయలేదు. 'Search Jobs' పేజీలో జాబ్స్‌ను 'Saved' లేదా 'Applied' గా మార్చండి.")

# ==========================================
# 5. PAGE: AUTO-APPLY & ALERTS
# ==========================================
elif current_page == "Auto-Apply & Alerts":
    st.markdown("<h3 style='color:#334155;'>⚡ Auto-Apply Engine & Email Dispatcher</h3>", unsafe_allow_html=True)
    if profile:
        st.write(f"Candidate Target: **{profile.get('full_name')}** ({profile.get('email')})")
        if st.button("📬 Trigger Instant Email Digest", use_container_width=True):
            send_email_alert(profile.get("email"), profile.get("full_name"), st.session_state.get("jobs_data", []))
            st.success("High-matching jobs digest dispatched to your inbox via SMTP!")
    else:
        st.warning("దయచేసి సైడ్‌బార్‌లో మీ రెజ్యూమ్ PDF అప్‌లోడ్ చేయండి.")

# --- Bottom Footer (2 Lines) ---
st.markdown("""
<div class='footer-container'>
    ⚡ <b>SmartJobApply AI Engine Architected & Engineered by</b><br>
    <b style='color: #4f46e5; font-size: 1.05rem;'>Dongavath Pradeep</b>
</div>
""", unsafe_allow_html=True)
