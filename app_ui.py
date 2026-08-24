import os
import sqlite3
import pandas as pd
import streamlit as st

from resume_parser import parse_resume
from job_search import search_jobs
from email_notifier import send_email_alert
from db_manager import init_db, store_candidate_profile, get_candidate_profile, update_job_status, get_job_statuses
from semantic_matcher import calculate_semantic_fit

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(page_title="SmartJobFinder | AI Career Intelligence", page_icon="⚡", layout="wide")
init_db()

# ============================================================
# THEME / CSS  (single source of truth — no duplicate injection)
# ============================================================
CUSTOM_CSS = """
<style>
:root {
    --accent-1: #38bdf8;
    --accent-2: #818cf8;
    --accent-3: #c084fc;
    --bg-card-top: rgba(30, 41, 59, 0.7);
    --bg-card-bot: rgba(15, 23, 42, 0.85);
    --border-soft: #334155;
    --text-muted: #94a3b8;
    --good: #10b981;
    --bad: #ef4444;
}

.stApp { background: radial-gradient(circle at 20% -10%, #0f172a 0%, #020617 60%); }

.gradient-title {
    background: linear-gradient(135deg, var(--accent-1) 0%, var(--accent-2) 50%, var(--accent-3) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 1.9rem;
    font-weight: 800;
    margin: 0;
    letter-spacing: -0.02em;
}

.header-wrap {
    padding-bottom: 14px;
    border-bottom: 1px solid var(--border-soft);
    margin-bottom: 22px;
}
.header-sub { margin: 4px 0 0 0; color: var(--text-muted); font-size: 0.9rem; }

.gradient-card {
    background: linear-gradient(145deg, var(--bg-card-top), var(--bg-card-bot));
    border: 1px solid rgba(56, 189, 248, 0.22);
    border-radius: 16px;
    padding: 20px 22px;
    margin-bottom: 16px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.28);
    transition: transform 0.18s ease, border-color 0.18s ease;
}
.gradient-card:hover {
    border-color: var(--accent-1);
    transform: translateY(-2px);
}

.job-title { color: #e2e8f0; margin: 0; font-size: 1.05rem; font-weight: 700; }
.job-meta { color: var(--text-muted); font-size: 0.86rem; margin: 4px 0 12px 0; }

.gradient-badge-match {
    background: linear-gradient(135deg, #059669, var(--good));
    color: #ffffff;
    font-weight: 800;
    padding: 4px 13px;
    border-radius: 20px;
    font-size: 0.82rem;
    white-space: nowrap;
    box-shadow: 0 2px 10px rgba(16, 185, 129, 0.3);
}

.tag-match, .tag-gap {
    padding: 3px 10px;
    border-radius: 6px;
    font-size: 0.76rem;
    font-weight: 600;
    margin: 2px 4px 2px 0;
    display: inline-block;
}
.tag-match {
    background: linear-gradient(135deg, rgba(6, 78, 59, 0.6), rgba(6, 95, 70, 0.8));
    border: 1px solid var(--good);
    color: #34d399;
}
.tag-gap {
    background: linear-gradient(135deg, rgba(127, 29, 29, 0.6), rgba(153, 27, 27, 0.8));
    border: 1px solid var(--bad);
    color: #f87171;
}

.sidebar-footer {
    text-align: center;
    color: var(--text-muted);
    font-size: 0.85rem;
    line-height: 1.7;
}
.sidebar-footer a { color: var(--accent-1); text-decoration: none; font-weight: 600; }

.footer-container {
    margin-top: 48px;
    padding: 20px;
    border-top: 1px solid var(--border-soft);
    text-align: center;
    color: var(--text-muted);
    font-size: 0.92rem;
    line-height: 1.6;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

DEFAULT_ROLES = "Python, Machine Learning, SQL"
JOB_STATUS_OPTIONS = ["Not Applied", "Applied", "Interviewing", "Saved"]

# ============================================================
# HELPERS
# ============================================================
def render_resume_upload():
    """Centered resume upload block in the main page body."""
    profile = get_candidate_profile()

    left, mid, right = st.columns([1, 2, 1])
    with mid:
        st.markdown("<h3 style='text-align:center; color:#38bdf8;'>📄 Upload Your Resume</h3>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Upload PDF Resume", type=["pdf"], label_visibility="collapsed")

        if uploaded_file and st.button("Parse & Generate Embeddings", use_container_width=True):
            temp_path = f"temp_{uploaded_file.name}"
            try:
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                profile_data = parse_resume(temp_path)
                if not profile_data or not profile_data.get("skills"):
                    st.warning("Resume parsed, but no skills were detected — check the file quality.")
                else:
                    store_candidate_profile(profile_data)
                    st.success("Candidate profile & vectors initialized!")
                    st.rerun()
            except Exception as e:
                st.error(f"Couldn't parse this resume: {e}")
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

        if profile:
            skills = profile.get("skills", [])
            ats = min(95, max(50, len(skills) * 12)) if skills else 30
            c_name = profile.get("full_name") or "Not set"
            c_email = profile.get("email") or "Not set"

            m1, m2 = st.columns(2)
            m1.metric("Candidate", c_name)
            m2.metric("Neural ATS Alignment", f"{ats}/100")
            st.progress(ats / 100)
            st.caption(f"Email: {c_email}")

            if skills:
                st.markdown("<div style='margin-top:8px;'><b>Extracted Skills:</b></div>", unsafe_allow_html=True)
                st.markdown("".join(f"<span class='tag-match'>{s}</span>" for s in skills), unsafe_allow_html=True)
        else:
            st.info("Upload a resume above to build your candidate profile.")

    return profile


def render_sidebar():
    profile = get_candidate_profile()

    with st.sidebar:
        if profile:
            st.markdown("<h4 style='color:#38bdf8;'>👤 Candidate Snapshot</h4>", unsafe_allow_html=True)
            skills = profile.get("skills", [])
            ats = min(95, max(50, len(skills) * 12)) if skills else 30
            st.metric("Neural ATS Alignment", f"{ats}/100")
            st.progress(ats / 100)
            st.markdown(f"**Name:** `{profile.get('full_name') or 'Not set'}`")
            st.markdown("<hr style='border:0.5px solid #334155;'>", unsafe_allow_html=True)

        st.markdown(
            """
            <div class='sidebar-footer'>
                <b>System Architect</b><br>
                <span style='color:#38bdf8; font-weight:bold;'>Dongavath Pradeep</span><br><br>
                <a href='https://github.com/DongavathPradeep' target='_blank'>🔗 GitHub</a><br>
                <a href='https://www.linkedin.com/in/pradeep-naik-42292b264/' target='_blank'>💼 LinkedIn</a>
            </div>
            """,
            unsafe_allow_html=True,
        )

    return profile


@st.cache_data(show_spinner=False, ttl=600)
def fetch_matched_jobs(_profile_key, role, location):
    """Cached so identical searches don't re-hit the job API / recompute embeddings."""
    raw = search_jobs(role=role, location=location)
    return raw


def get_jobs(profile, role_query, location_query, force_refresh=False):
    cache_key = f"{profile.get('email','anon')}|{role_query}|{location_query}"
    if force_refresh or st.session_state.get("last_query_key") != cache_key:
        with st.spinner("Analyzing resume skills & computing semantic match across live jobs..."):
            raw = fetch_matched_jobs(cache_key, role_query, location_query)
            st.session_state["jobs_data"] = calculate_semantic_fit(profile, raw)
            st.session_state["last_query_key"] = cache_key
    return st.session_state.get("jobs_data", [])


def render_job_card(job, idx, statuses):
    matched_html = "".join(f"<span class='tag-match'>✓ {s}</span>" for s in job.get("matched_skills", [])) or "None detected"
    missing_html = "".join(f"<span class='tag-gap'>✗ {s}</span>" for s in job.get("missing_skills", [])) or "<span style='color:#34d399;'>None</span>"

    st.markdown(
        f"""
        <div class='gradient-card'>
            <div style='display:flex; justify-content:space-between; align-items:center; gap:12px;'>
                <h4 class='job-title'>{job.get('title')}</h4>
                <span class='gradient-badge-match'>{job.get('semantic_score')}% Match</span>
            </div>
            <p class='job-meta'><b>{job.get('company')}</b> • {job.get('location')}</p>
            <div style='margin-bottom:6px;'><b>Direct Skill Matches:</b><br>{matched_html}</div>
            <div><b>Skill Gaps to Cover:</b><br>{missing_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns([3, 1])
    if job.get("url"):
        c1.markdown(f"[🚀 **Apply via Portal**]({job.get('url')})")

    job_key = f"{job.get('title')}--{job.get('company')}"
    current_status = statuses.get(job_key, "Not Applied")
    default_index = JOB_STATUS_OPTIONS.index(current_status) if current_status in JOB_STATUS_OPTIONS else 0

    new_status = c2.selectbox("Status", JOB_STATUS_OPTIONS, index=default_index, key=f"st_{idx}", label_visibility="collapsed")
    if new_status != current_status:
        update_job_status(job.get("title"), job.get("company"), new_status)
        st.rerun()


# ============================================================
# MAIN
# ============================================================
if "jobs_data" not in st.session_state:
    st.session_state["jobs_data"] = []

render_sidebar()
profile = render_resume_upload()
st.markdown("<hr style='border:0.5px solid #334155; margin: 8px 0 24px 0;'>", unsafe_allow_html=True)

tab_feed, tab_analytics, tab_roadmap, tab_tracker, tab_alerts = st.tabs(
    ["🎯 Resume-Matched Jobs", "📊 Gap Intelligence", "🗺️ 7-Day Bridge Roadmap", "📋 Application Tracker", "📬 Automation & SMTP"]
)

# ---------------- TAB 1: MATCHED JOBS ----------------
with tab_feed:
    candidate_skills = profile.get("skills", []) if profile else []
    default_role = ", ".join(candidate_skills[:3]) if candidate_skills else DEFAULT_ROLES

    col1, col2, col3, col4 = st.columns([2.2, 1.1, 1.1, 0.9])
    role_query = col1.text_input(
        "Target Roles / Skill Set (Auto-loaded from Resume)",
        value=default_role,
        help="Matches jobs directly according to the skills found in your uploaded resume",
    )
    exp_level = col2.selectbox("Experience", ["Fresher / Entry Level", "1-3 yrs", "4+ yrs", "All"])
    location_query = col3.selectbox("Location", ["Hyderabad", "Bangalore", "Pune", "Chennai", "Remote"])
    refresh_clicked = col4.button("🚀 Fetch Matched Jobs", use_container_width=True)

    if not profile:
        st.warning("⚠️ Please upload your resume in the sidebar first!")
        results = []
    else:
        results = get_jobs(profile, role_query, location_query, force_refresh=refresh_clicked)

    statuses = get_job_statuses()

    if results:
        m1, m2, m3 = st.columns(3)
        m1.metric("Roles Evaluated", len(results))
        avg_score = round(sum(j.get("semantic_score", 0) for j in results) / len(results), 1)
        m2.metric("Mean Semantic Match", f"{avg_score}%")
        m3.metric("High Match Roles (≥70%)", len([j for j in results if j.get("semantic_score", 0) >= 70]))

        for idx, job in enumerate(results):
            render_job_card(job, idx, statuses)
    elif profile:
        st.info("No jobs yet — click **Fetch Matched Jobs** to run a search.")

# ---------------- TAB 2: GAP INTELLIGENCE ----------------
with tab_analytics:
    results = st.session_state.get("jobs_data", [])
    if results:
        all_missing = [s for j in results for s in j.get("missing_skills", [])]
        if all_missing:
            st.caption("Top Missing Market Skills by Frequency")
            st.bar_chart(pd.Series(all_missing).value_counts().head(8))
        else:
            st.success("High semantic alignment across all skills — no consistent gaps found!")
    else:
        st.info("Upload your resume and fetch jobs to view gap analytics.")

# ---------------- TAB 3: ROADMAP ----------------
with tab_roadmap:
    st.markdown("#### 🗺️ 7-Day Targeted Upskilling Bridge")
    st.write(
        "Day 1-2: Core Foundations & Frameworks | Day 3-4: Build Vector Pipeline Project | "
        "Day 5-6: Integration & Deployment | Day 7: Re-index Profile"
    )

# ---------------- TAB 4: APPLICATION TRACKER ----------------
with tab_tracker:
    try:
        conn = sqlite3.connect("candidate.db")
        df_track = pd.read_sql(
            "SELECT job_title AS 'Role', company AS 'Company', status AS 'Status', updated_at AS 'Updated' "
            "FROM applications ORDER BY updated_at DESC",
            conn,
        )
        conn.close()
    except Exception as e:
        df_track = pd.DataFrame()
        st.error(f"Couldn't load application history: {e}")

    if not df_track.empty:
        st.dataframe(df_track, use_container_width=True)
    else:
        st.info("No applications logged yet. Search jobs and mark status as 'Applied' or 'Saved'.")

# ---------------- TAB 5: AUTOMATION & SMTP ----------------
with tab_alerts:
    st.markdown("### 📬 Email Automation & SMTP Gateway")
    if profile:
        target_email = profile.get("email")
        target_name = profile.get("full_name") or "Candidate"

        if not target_email:
            st.warning("⚠️ No email found on your parsed resume — add one before sending digests.")
        else:
            st.markdown(f"**Target Candidate:** `{target_name}`")
            st.markdown(f"**Destination Inbox:** <code style='color:#34d399;'>{target_email}</code>", unsafe_allow_html=True)
            st.markdown(f"**Queued Matched Roles:** `{len(st.session_state.get('jobs_data', []))}`")

            if st.button("🚀 Trigger Email Digest Now", use_container_width=True):
                current_jobs = st.session_state.get("jobs_data", [])
                if current_jobs:
                    with st.spinner("Dispatching email digest via SMTP..."):
                        send_error = None
                        try:
                            success = send_email_alert(target_email, target_name, current_jobs)
                        except Exception as e:
                            success = False
                            send_error = str(e)

                        if success:
                            st.success(f"✅ High-match job digest sent to {target_email}!")
                        elif send_error:
                            st.error(f"SMTP error: {send_error}")
                        else:
                            st.error("❌ Failed to send email. Check your SMTP App Password configuration.")
                else:
                    st.warning("⚠️ No jobs in queue! Fetch jobs in the first tab first.")
    else:
        st.warning("⚠️ Please upload your resume in the sidebar to configure the candidate profile.")

# ---------------- FOOTER ----------------
st.markdown(
    """
    <div class='footer-container'>
        ⚡ <b>SmartJobFinder AI Engine — Architected &amp; Engineered by</b><br>
        <b style='color:#38bdf8; font-size:1.05rem;'>Dongavath Pradeep</b>
    </div>
    """,
    unsafe_allow_html=True,
)
