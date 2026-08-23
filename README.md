# 🤖 Autonomous AI Job Application Agent

A Python-based intelligent job discovery and application assistant that analyzes candidate resumes, extracts relevant skills, evaluates job suitability against live openings, dispatches automated email alerts, and assists in auto-applying using browser automation.

---

## 📌 Project Overview

The **Autonomous AI Job Agent** simplifies and automates the job search workflow:
1. Reads a resume in PDF format and extracts candidate profile and technical skills.
2. Stores structured candidate data in a local SQLite database for instant retrieval.
3. Retrieves relevant job listings through an external Job Search API (with local JSON fallback).
4. Compares the candidate's skills with required job skills, calculates a match score, identifies missing skill gaps, and ranks recommendations.
5. Continuously monitors for high-matching roles (≥75%) and sends automated email digests via background workers.
6. Launches an assisted browser workflow with Selenium to pre-fill application forms and attach resumes.

---

## 🚀 Key Features

* 📄 **Resume PDF Processing** — Reads and extracts candidate contact details and skills from PDF files.
* 🗄️ **Persistent Database Storage** — Saves structured profiles locally in SQLite to prevent repetitive parsing.
* 🔎 **Job Search & API Integration** — Searches jobs based on target roles with automatic JSON fallback.
* 🎯 **Skill Matching Engine** — Compares candidate skills against job requirements in real time.
* ❌ **Missing Skill Detection** — Isolates specific competencies the candidate needs to learn.
* 📊 **Match Score Calculation** — Calculates job suitability as a clear percentage.
* 🏆 **Job Ranking & Recommendations** — Sorts and displays open positions by highest match score.
* 📧 **Automated Email Alerts** — Background daemon periodically monitors and emails formatted job digests using Gmail SMTP.
* 🌐 **Assisted Auto-Apply** — Uses Selenium WebDriver to launch target application forms, populate candidate data, attach resumes, and hold for human review before submission.

---

## 🛠️ Tech Stack

* **Programming Language:** Python 3.x
* **Browser Automation:** Selenium, WebDriver Manager
* **PDF Processing:** PyPDF
* **Database:** SQLite3
* **Scheduling & Background Tasks:** Schedule
* **HTTP/API Requests:** Requests
* **Email Protocols:** SMTPLib, Email MIME
* **Version Control:** Git & GitHub

---

## 📂 Project Structure

```text
AI-Job-Agent/
│
├── main.py               # Interactive CLI workflow orchestrator
├── job_alert_bot.py      # Background scheduled worker for automated email alerts
├── auto_apply.py         # Selenium browser automation & assisted form-filler
├── resume_parser.py      # PDF text parsing & skill extraction engine
├── job_search.py         # Job retrieval engine (Live API + fallback)
├── email_notifier.py     # HTML email builder & SMTP notification dispatcher
├── db.py                 # SQLite database initialization & profile management
├── jobs.json             # Mock dataset for offline execution
├── requirements.txt      # Project dependencies list
└── README.md             # Project documentation



  
  **### ⚙️How It Works**
  

Candidate Resume (PDF)
         ↓
Extract Resume Text & Skills (PyPDF)
         ↓
Store Candidate Profile in SQLite DB
         ↓
User Enters Target Job Role
         ↓
Search Job Listings (API / JSON)
         ↓
Compare Required Skills & Find Missing Skills
         ↓
Calculate Match Score & Rank Jobs
         ↓
   ┌─────────────────────────────┐
   │    Decision Orchestration   │
   └──────────────┬──────────────┘
                  │
         ┌────────┴────────┐
         ▼                 ▼
  [Interactive CLI]   [Background Bot]
         │                 │
  Selenium Browser    Scheduled Email
  Auto-Apply Assist   Digest via SMTP

### 💻 Example Terminal Output

============================================================
🤖 AUTONOMOUS AI JOB AGENT - WORKFLOW ORCHESTRATOR
============================================================

📂 Existing candidate profile detected: PRADEEP NAIK DONGAVATH
Do you want to use the saved profile? (y/n): y

--- Current Candidate Profile ---
👤 Name   : PRADEEP NAIK DONGAVATH
📧 Email  : candidate@example.com
📞 Phone  : +91-XXXXXXXXXX
🛠️ Skills : Python, SQL, HTML, CSS, Git
-----------------------------------

🔍 What job role are you looking for? (or type 'exit' to quit): Python Developer
🌐 Scanning open listings for 'Python Developer'...

==================================================
🎯 MATCH OPTION [1/4]:
📌 Job Title      : Python Developer
🏢 Company        : Tech Innovators
📊 Match Score    : 100.0%
✅ Matching Skills: Python, SQL, HTML, CSS
⚠️ Missing Skills : None
🔗 Portal Link    : [https://example.com/apply](https://example.com/apply)
==================================================

👉 Would you like to apply for this job? [y = Apply, n = Next Job, s = Search Another Role]:


🎯 Learning Outcomes
Through this project, practical experience was gained in:

Modular Python application design and clean code architecture.

Browser automation workflows using Selenium WebDriver.

PDF text extraction and entity parsing using PyPDF and regular expressions.

Persistent data management with SQLite3.

REST API integration, response handling, and resilient offline fallback logic.

Background scheduling using Schedule and automated HTML email alerts via SMTPLib.

Version control and repository documentation with Git & GitHub.

### 👨‍💻 Author

Dongavath Pradeep Naik

B.Tech — Computer Science & Engineering

Focus Areas: Python Development, Data Analytics, and Autonomous AI Agents

📄 License

This project is open-source and intended for educational and portfolio purposes.
