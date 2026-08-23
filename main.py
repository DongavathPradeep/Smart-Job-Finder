import os
from db import init_db, get_latest_candidate_profile
from job_search import search_jobs
from email_notifier import send_email_alert

def calculate_match_score(candidate_skills: list, job_description: str, job_title: str) -> tuple[float, list, list]:
    candidate_skills_lower = {s.lower().strip() for s in candidate_skills}
    text = f"{job_title} {job_description}".lower()
    
    matched = [s for s in candidate_skills if s.lower().strip() in text]
    
    # Common tech skills to check for gaps
    tech_keywords = [
        "python", "django", "fastapi", "flask", "sql", "postgresql", "mysql", 
        "docker", "aws", "git", "rest api", "pandas", "numpy", "react", "javascript", 
        "machine learning", "selenium", "html", "css"
    ]
    
    required_in_job = [kw for kw in tech_keywords if kw in text]
    missing = [req for req in required_in_job if req not in candidate_skills_lower]
    
    if required_in_job:
        score = (len(matched) / len(required_in_job)) * 100
    else:
        score = 80.0 if matched else 40.0
        
    return min(100.0, round(score, 2)), matched, missing

def score_jobs(candidate_skills: list, jobs: list) -> list:
    scored_jobs = []
    for job in jobs:
        score, matched, missing = calculate_match_score(
            candidate_skills, 
            job.get("description", ""), 
            job.get("title", "")
        )
        job_copy = dict(job)
        job_copy["match_score"] = score
        job_copy["matched_skills"] = matched
        job_copy["missing_skills"] = missing
        scored_jobs.append(job_copy)
        
    scored_jobs.sort(key=lambda x: x.get("match_score", 0), reverse=True)
    return scored_jobs

if __name__ == "__main__":
    init_db()
    profile = get_latest_candidate_profile()
    if profile:
        print(f"Loaded profile: {profile.get('full_name')}")
        jobs = search_jobs(role="Python Developer", location="Hyderabad")
        results = score_jobs(profile.get("skills", []), jobs)
        print(f"Scored {len(results)} jobs.")
    else:
        print("No profile found. Run parser first.")
