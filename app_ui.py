import streamlit as st
import os

from resume_parser import parse_resume
from db import init_db, store_candidate_profile, get_candidate_profile
from job_search import search_jobs
from main import score_jobs
from email_notifier import send_email_alert

# Initialize database
init_db()

st.set_page_config(
    page_title="AI Job Application Agent",
    page_icon="💼",
    layout="wide"
)

st.title("💼 Autonomous AI Job Discovery & Apply Agent")
st.caption("Automate job discovery, match scores, location filters, and email digests.")

# Sidebar: Resume Ingestion & Profile Status
with st.sidebar:
    st.header("📄 Candidate Profile")
    uploaded_file = st.file_uploader("Upload your PDF Resume", type=["pdf"])
    
    if uploaded_file is not None:
        if st.button("Ingest Resume", use_container_width=True):
            with st.spinner("Parsing resume and storing in SQLite..."):
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

# Main Screen: Job Discovery & Scoring
st.subheader("🔍 Job Match Engine")
col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    role_query = st.text_input("Target Job Role", value="Python Developer", placeholder="e.g. Python Developer, Data Analyst")
with col2:
    location_query = st.selectbox(
        "Preferred Location",
        ["Hyderabad", "Bangalore", "Pune", "Chennai", "Mumbai", "Noida", "Gurgaon", "Remote"]
    )
with col3:
    st.write("")
    st.write("")
    search_btn = st.button("Search Jobs", use_container_width=True, type="primary")

if search_btn and role_query:
    profile = get_candidate_profile()
    if not profile:
        st.error("Candidate profile not found. Please upload your resume from the left sidebar first.")
    else:
        with st.spinner(f"Fetching '{role_query}' jobs in '{location_query}'..."):
            raw_jobs = search_jobs(role=role_query, location=location_query)
            results = score_jobs(profile.get("skills", []), raw_jobs)
            
            st.write(f"Found **{len(results)}** active opportunities in **{location_query}** for **{profile.get('full_name')}**:")
            
            for job in results:
                with st.container(border=True):
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.markdown(f"### {job.get('title')}")
                        st.markdown(f"**Company:** {job.get('company')} | **Location:** {job.get('location')}")
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
            with st.spinner(f"Dispatching SMTP digest for {location_query}..."):
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
                        st.success(f"Email sent successfully to {profile.get('email')}!")
                    else:
                        st.error("Failed to send email. Check credentials.")
                else:
                    st.warning("No jobs matched the score threshold.")
