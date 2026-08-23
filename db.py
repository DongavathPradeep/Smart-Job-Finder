import json
import sqlite3

DB_NAME = "agent_database.db"


def init_db():
    """Initialize candidate and application tracking tables."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT,
            email TEXT,
            phone TEXT,
            skills TEXT,
            resume_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )
    conn.commit()
    conn.close()


def save_candidate_profile(profile):
    """Save or update candidate profile."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO candidates (full_name, email, phone, skills, resume_path)
        VALUES (?, ?, ?, ?, ?)
    """,
        (
            profile["full_name"],
            profile["email"],
            profile["phone"],
            json.dumps(profile["skills"]),
            profile["resume_path"],
        ),
    )
    conn.commit()
    conn.close()


def get_latest_candidate_profile():
    """Retrieve the most recently saved profile."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT full_name, email, phone, skills, resume_path FROM candidates ORDER BY id DESC LIMIT 1"
    )
    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "full_name": row[0],
            "email": row[1],
            "phone": row[2],
            "skills": json.loads(row[3]),
            "resume_path": row[4],
            "cover_letter": f"Hi, I am {row[0]}. I have strong practical skills in {', '.join(json.loads(row[3])[:4])} and I am excited to apply for this opportunity.",
        }
    return None