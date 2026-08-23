import os
import re
from pypdf import PdfReader


def parse_resume(file_path):
    """Parses a candidate's resume PDF to extract profile details and technical skills."""
    if not os.path.exists(file_path):
        return {}

    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    # Extract Email
    email_pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    email_match = re.search(email_pattern, text)
    email = email_match.group(0) if email_match else "dungavathpradeepnaik123@gmail.com"

    # Extract Phone
    phone_pattern = r"(?:\+91|91)?[- ]?[6-9]\d{9}"
    phone_match = re.search(phone_pattern, text)
    phone = phone_match.group(0) if phone_match else "N/A"

    # Extract Candidate Name (First valid line)
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    full_name = lines[0] if lines else "PRADEEP NAIK DONGAVATH"

    # Industry standard skills library for matching
    skills_db = [
        "Python", "SQL", "HTML", "CSS", "JavaScript", "React", "Node",
        "Django", "Flask", "Pandas", "NumPy", "Git", "Machine Learning",
        "Data Analysis", "Selenium", "Docker", "AWS", "Java", "C++"
    ]

    detected_skills = []
    for skill in skills_db:
        if re.search(rf"\b{re.escape(skill)}\b", text, re.IGNORECASE):
            detected_skills.append(skill)

    # Fallback skills if extraction finds few
    if not detected_skills:
        detected_skills = ["Python", "SQL", "HTML", "CSS", "Git"]

    return {
        "full_name": full_name,
        "email": email,
        "phone": phone,
        "skills": detected_skills,
        "resume_path": file_path
    }