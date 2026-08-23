import requests
import streamlit as st

API_BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="AI Job Application Agent", page_icon="💼", layout="wide"
)

st.title("💼 Autonomous AI Job Discovery & Apply Agent")
st.caption(
    "Automate your job search, filter by preferred locations, analyze skill"
    " matches, and trigger workflows."
)

# Sidebar: Resume Ingestion & Profile Status
with st.sidebar:
    st.header("📄 Candidate Profile")
    uploaded_file = st.file_uploader("Upload your PDF Resume", type=["pdf"])

    if uploaded_file is not None:
        if st.button("Ingest Resume", use_container_width=True):
            with st.spinner("Parsing resume and storing in SQLite..."):
                files = {
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        "application/pdf",
                    )
                }
                res = requests.post(
                    f"{API_BASE_URL}/api/resume/upload", files=files
                )
                if res.status_code == 200:
                    st.success("Resume parsed successfully!")
                else:
                    st.error("Failed to process resume.")

    st.markdown("---")
    if st.button("Load Stored Profile", use_container_width=True):
        res = requests.get(f"{API_BASE_URL}/api/candidate/profile")
        if res.status_code == 200:
            profile = res.json()
            st.write(f"**Name:** {profile.get('full_name')}")
            st.write(f"**Email:** {profile.get('email')}")
            st.write(f"**Phone:** {profile.get('phone')}")
            st.write("**Extracted Skills:**")
            st.info(", ".join(profile.get("skills", [])))
        else:
            st.warning("No candidate profile found in database.")

# Main Screen: Job Discovery & Scoring
st.subheader("🔍 Job Match Engine")
col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    role_query = st.text_input(
        "Target Job Role",
        value="Python Developer",
        placeholder="e.g. Python Developer, Data Analyst",
    )
with col2:
    location_query = st.selectbox(
        "Preferred Location",
        [
            "Hyderabad",
            "Bangalore",
            "Pune",
            "Chennai",
            "Mumbai",
            "Noida",
            "Gurgaon",
            "Remote",
        ],
    )
with col3:
    st.write("")
    st.write("")
    search_btn = st.button(
        "Search Jobs", use_container_width=True, type="primary"
    )

if search_btn and role_query:
    with st.spinner(
        f"Evaluating opportunities for '{role_query}' in '{location_query}'..."
    ):
        res = requests.post(
            f"{API_BASE_URL}/api/jobs/match",
            json={"role": role_query, "location": location_query},
        )

        if res.status_code == 200:
            data = res.json()
            results = data.get("results", [])
            st.write(
                f"Found **{len(results)}** active opportunities in"
                f" **{location_query}** for **{data.get('candidate')}**:"
            )

            for job in results:
                with st.container(border=True):
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.markdown(f"### {job.get('title')}")
                        st.markdown(
                            f"**Company:** {job.get('company')} |"
                            f" **Location:** {job.get('location')}"
                        )
                        st.write(
                            "**Matched Skills:** "
                            + ", ".join(job.get("matched_skills", []))
                        )
                        if job.get("missing_skills"):
                            st.write(
                                "**Skill Gaps (To Learn):** "
                                + ", ".join(job.get("missing_skills", []))
                            )
                    with c2:
                        score = int(job.get("match_score", 0))
                        st.metric(label="Match Score", value=f"{score}%")
                        st.progress(score / 100)

                        if st.button(
                            "Auto-Fill Application",
                            key=f"apply_{job.get('title')}_{job.get('company')}_{score}",
                        ):
                            apply_res = requests.post(
                                f"{API_BASE_URL}/api/jobs/apply",
                                json={"job_url": job.get("url")},
                            )
                            if apply_res.status_code == 200:
                                st.toast(
                                    "Selenium browser automation launched!",
                                    icon="🚀",
                                )
        else:
            st.error(
                "Unable to retrieve job matches. Ensure a profile is uploaded."
            )

st.markdown("---")
# Email Digest Section
st.subheader("📬 Automated Location Alerts")
alert_col1, alert_col2 = st.columns([3, 1])
with alert_col1:
    threshold = st.slider(
        "Minimum Match Score Threshold (%)",
        min_value=50,
        max_value=100,
        value=75,
    )
with alert_col2:
    st.write("")
    st.write("")
    if st.button("Trigger Email Digest", use_container_width=True):
        with st.spinner(f"Dispatching SMTP digest for {location_query}..."):
            alert_res = requests.post(
                f"{API_BASE_URL}/api/jobs/trigger-alerts",
                json={
                    "target_roles": [role_query],
                    "location": location_query,
                    "min_score_threshold": threshold,
                },
            )
            if alert_res.status_code == 200:
                st.success(
                    f"HTML digest email for {location_query} queued"
                    " successfully!"
                )
            else:
                st.error("Failed to trigger email alerts.")