import json
import sqlite3

DB_PATH = "candidate.db"


def init_db():
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS candidate (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT,
            email TEXT,
            phone TEXT,
            skills TEXT,
            summary TEXT
        )
    """)
  conn.commit()
  conn.close()


def store_candidate_profile(data: dict):
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()
  cursor.execute("DELETE FROM candidate")  # Keep only latest profile

  skills_json = json.dumps(data.get("skills", []))
  cursor.execute(
      """
        INSERT INTO candidate (full_name, email, phone, skills, summary)
        VALUES (?, ?, ?, ?, ?)
    """,
      (
          data.get("full_name", "Anonymous Candidate"),
          data.get("email", ""),
          data.get("phone", ""),
          skills_json,
          data.get("summary", ""),
      ),
  )
  conn.commit()
  conn.close()


def get_candidate_profile() -> dict:
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()
  cursor.execute(
      "SELECT full_name, email, phone, skills, summary FROM candidate ORDER BY"
      " id DESC LIMIT 1"
  )
  row = cursor.fetchone()
  conn.close()

  if not row:
    return {}

  return {
    "full_name": row[0],
    "email": row[1],
    "phone": row[2],
    "skills": json.loads(row[3]) if row[3] else [],
    "summary": row[4],
  }
