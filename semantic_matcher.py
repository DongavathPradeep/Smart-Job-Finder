import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st

@st.cache_resource
def load_embedding_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

def calculate_semantic_fit(candidate_profile: dict, job_postings: list) -> list:
    if not job_postings or not candidate_profile:
        return job_postings

    model = load_embedding_model()

    candidate_skills_str = ", ".join(candidate_profile.get("skills", []))
    candidate_summary = candidate_profile.get("summary", "")
    candidate_context = f"Skills: {candidate_skills_str}. Experience & Summary: {candidate_summary}"

    candidate_vector = model.encode([candidate_context])

    tech_keywords = [
        "python", "django", "fastapi", "flask", "sql", "postgresql", "mysql", "mongodb",
        "docker", "kubernetes", "aws", "azure", "gcp", "git", "github", "rest api", "graphql",
        "pandas", "numpy", "react", "javascript", "typescript", "machine learning", "deep learning",
        "selenium", "html", "css", "tailwind", "linux", "ci/cd", "redis", "celery", "airflow"
    ]
    candidate_skills_lower = {s.lower().strip() for s in candidate_profile.get("skills", [])}

    scored_jobs = []
    job_texts = [f"{j.get('title', '')} {j.get('description', '')}" for j in job_postings]
    job_vectors = model.encode(job_texts)

    similarities = cosine_similarity(candidate_vector, job_vectors)[0]

    for idx, job in enumerate(job_postings):
        text = job_texts[idx].lower()
        matched = [s for s in candidate_profile.get("skills", []) if s.lower().strip() in text]
        required = [kw for kw in tech_keywords if kw in text]
        missing = [req for req in required if req not in candidate_skills_lower]

        raw_sim = float(similarities[idx])
        semantic_score = min(98.5, max(35.0, round(raw_sim * 100, 1)))

        job_copy = dict(job)
        job_copy["semantic_score"] = semantic_score
        job_copy["matched_skills"] = list(dict.fromkeys(matched))
        job_copy["missing_skills"] = list(dict.fromkeys(missing))
        scored_jobs.append(job_copy)

    return sorted(scored_jobs, key=lambda x: x.get("semantic_score", 0), reverse=True)