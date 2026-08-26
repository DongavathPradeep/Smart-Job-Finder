import io
import re
from pypdf import PdfReader

def parse_resume(file_input):
    """
    file_input can be a file path string or bytes/BytesIO from Streamlit.
    """
    if isinstance(file_input, bytes):
        stream = io.BytesIO(file_input)
    elif hasattr(file_input, "read"):
        file_input.seek(0)
        stream = io.BytesIO(file_input.read())
    else:
        stream = file_input

    reader = PdfReader(stream)
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"

    # Email Extraction
    email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
    email = email_match.group(0) if email_match else "dungavathpradeepnaik123@gmail.com"

    # Name Extraction fallback
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    full_name = lines[0] if lines else "Pradeep Naik"
    if len(full_name) > 35 or "@" in full_name:
        full_name = "Pradeep Naik"

    # Skills Detection
    SKILLS_DB = [
        "python", "java", "c++", "c", "sql", "html", "css", "javascript", "react", "angular",
        "node", "express", "django", "flask", "fastapi", "machine learning", "deep learning",
        "nlp", "data science", "data analysis", "pandas", "numpy", "scikit-learn", "tensorflow",
        "pytorch", "aws", "azure", "gcp", "docker", "kubernetes", "git", "linux", "selenium"
    ]
    
    found_skills = []
    text_lower = text.lower()
    for skill in SKILLS_DB:
        if re.search(r"\b" + re.escape(skill) + r"\b", text_lower):
            found_skills.append(skill.title())

    if not found_skills:
        found_skills = ["Python", "SQL", "Machine Learning"]

    return {
        "full_name": full_name,
        "email": email,
        "skills": list(set(found_skills)),
        "raw_text": text
    }
