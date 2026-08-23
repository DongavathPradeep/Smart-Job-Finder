import os
import requests
import re
import json
from dotenv import load_dotenv

load_dotenv()

ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")

KNOWN_SKILLS = [
    "Python", "Java", "JavaScript", "C++", "SQL", "HTML", "CSS",
    "React", "Angular", "Node.js", "Django", "FastAPI", "Flask",
    "AWS", "Azure", "Docker", "Kubernetes", "Machine Learning",
    "Data Analysis", "Pandas", "NumPy", "Git"
]

def extract_skills(text: str) -> list:
    skills_found = []
    for s in KNOWN_SKILLS:
        if re.search(rf"\b{re.escape(s)}\b", text, re.IGNORECASE):
            skills_found.append(s)
    return list(set(skills_found)) if skills_found else ["Python", "SQL"]

def search_jobs(role: str, location: str = "India", results_per_page: int = 10) -> list:
    """Fetches jobs based on exact city like Hyderabad, Bangalore, Pune, etc."""
    if ADZUNA_APP_ID and ADZUNA_APP_KEY:
        try:
            url = "https://api.adzuna.com/v1/api/jobs/in/search/1"
            params = {
                "app_id": ADZUNA_APP_ID.strip(),
                "app_key": ADZUNA_APP_KEY.strip(),
                "what": role,
                "where": location,
                "results_per_page": results_per_page,
                "content-type": "application/json"
            }
            res = requests.get(url, params=params, timeout=10)
            if res.status_code == 200:
                data = res.json()
                jobs = []
                for item in data.get("results", []):
                    desc = item.get("description", "")
                    skills = extract_skills(desc + " " + item.get("title", ""))
                    jobs.append({
                        "title": item.get("title", "").replace("<strong>", "").replace("</strong>", ""),
                        "company": item.get("company", {}).get("display_name", "Leading Enterprise"),
                        "location": item.get("location", {}).get("display_name", location),
                        "url": item.get("redirect_url"),
                        "skills": skills,
                        "description": desc[:250] + "..."
                    })
                if jobs:
                    return jobs
        except Exception as e:
            print(f"⚠️ Live search failed for {location}: {e}")

    # Fallback to local data
    if os.path.exists("jobs.json"):
        with open("jobs.json", "r") as f:
            return json.load(f)
    return []