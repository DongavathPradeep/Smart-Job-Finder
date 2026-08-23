import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional

from resume_parser import parse_resume
from db import init_db, store_candidate_profile, get_candidate_profile
from job_search import search_jobs
from main import score_jobs
from email_notifier import send_email_alert
from auto_apply import apply_to_job

app = FastAPI(
    title="Autonomous AI Job Agent API",
    description="Backend API for Resume Parsing, Job Matching, Alerts, and Auto-Apply Automation",
    version="1.0.0"
)

# Initialize database schema on startup
@app.on_event("startup")
def startup_event():
    init_db()

# --- Pydantic Schemas ---

class JobSearchRequest(BaseModel):
    role: str
    location: Optional[str] = "Hyderabad"

class ApplyRequest(BaseModel):
    job_url: str

class AlertTriggerRequest(BaseModel):
    target_roles: List[str]
    location: Optional[str] = "Hyderabad"
    min_score_threshold: Optional[float] = 75.0


# --- Endpoints ---

@app.post("/api/resume/upload")
async def upload_resume(file: UploadFile = File(...)):
    """Accepts PDF resume, extracts skills & contact info, saves to SQLite."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    temp_path = f"temp_{file.filename}"
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        parsed_data = parse_resume(temp_path)
        store_candidate_profile(parsed_data)
        
        return {
            "status": "success",
            "message": "Resume parsed and profile saved successfully.",
            "data": parsed_data
        }
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


@app.get("/api/candidate/profile")
def get_profile():
    """Retrieves the currently stored candidate profile."""
    profile = get_candidate_profile()
    if not profile:
        raise HTTPException(status_code=404, detail="No candidate profile found. Please upload a resume first.")
    return profile


@app.post("/api/jobs/match")
def match_jobs_endpoint(req: JobSearchRequest):
    """Fetches jobs based on role & location, scores them against candidate skills."""
    profile = get_candidate_profile()
    if not profile:
        raise HTTPException(status_code=404, detail="Candidate profile not found. Please upload a resume first.")
    
    raw_jobs = search_jobs(role=req.role, location=req.location)
    scored = score_jobs(profile.get("skills", []), raw_jobs)
    
    return {
        "candidate": profile.get("full_name"),
        "role_queried": req.role,
        "location": req.location,
        "total_jobs": len(scored),
        "results": scored
    }


@app.post("/api/jobs/trigger-alerts")
def trigger_alerts(req: AlertTriggerRequest, background_tasks: BackgroundTasks):
    """Scans jobs across roles & location, sends HTML digest email in background."""
    profile = get_candidate_profile()
    if not profile:
        raise HTTPException(status_code=404, detail="Candidate profile not found.")
    
    all_matched_jobs = []
    for role in req.target_roles:
        jobs = search_jobs(role=role, location=req.location)
        scored = score_jobs(profile.get("skills", []), jobs)
        qualified = [j for j in scored if j.get("match_score", 0) >= req.min_score_threshold]
        all_matched_jobs.extend(qualified)
    
    if not all_matched_jobs:
        return {"message": "No jobs met the score threshold. No email dispatched."}
    
    background_tasks.add_task(
        send_email_alert,
        recipient_email=profile.get("email"),
        candidate_name=profile.get("full_name"),
        matched_jobs=all_matched_jobs
    )
    
    return {
        "status": "queued",
        "message": f"Alert email queued for {profile.get('email')}",
        "matched_count": len(all_matched_jobs)
    }


@app.post("/api/jobs/apply")
def trigger_auto_apply(req: ApplyRequest, background_tasks: BackgroundTasks):
    """Triggers Selenium automation to fill and submit job applications."""
    profile = get_candidate_profile()
    if not profile:
        raise HTTPException(status_code=404, detail="Candidate profile not found.")
    
    background_tasks.add_task(apply_to_job, req.job_url, profile)
    return {
        "message": "Selenium automation initiated in the background.",
        "target_url": req.job_url
    }