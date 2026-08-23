import os
from auto_apply import auto_fill_job_application
from db import get_latest_candidate_profile, init_db, save_candidate_profile
from job_search import search_jobs
from resume_parser import parse_resume


def main():
    print("=" * 60)
    print("🤖 AUTONOMOUS AI JOB AGENT - WORKFLOW ORCHESTRATOR")
    print("=" * 60)

    init_db()

    candidate_profile = get_latest_candidate_profile()

    if candidate_profile:
        print(
            f"\n📂 Existing candidate profile detected: {candidate_profile.get('full_name')}"
        )
        choice = (
            input("Do you want to use the saved profile? (y/n): ")
            .strip()
            .lower()
        )
        if choice != "y":
            candidate_profile = None

    if not candidate_profile:
        resume_file = input(
            "\nEnter your Resume PDF filename (e.g., resume.pdf): "
        ).strip()
        if not os.path.exists(resume_file):
            print(
                f"❌ File '{resume_file}' not found in current directory!"
            )
            return

        print("\n🔍 Parsing candidate resume...")
        parsed_data = parse_resume(resume_file)
        parsed_data["resume_path"] = resume_file

        save_candidate_profile(parsed_data)
        candidate_profile = parsed_data
        print(
            "✅ Candidate profile parsed and stored in database successfully!"
        )

    print("\n--- Current Candidate Profile ---")
    print(f"👤 Name   : {candidate_profile.get('full_name')}")
    print(f"📧 Email  : {candidate_profile.get('email')}")
    print(f"📞 Phone  : {candidate_profile.get('phone')}")
    print(f"🛠️ Skills : {', '.join(candidate_profile.get('skills', []))}")
    print("-" * 35)

    candidate_skills = candidate_profile.get("skills", [])

    while True:
        job_role = input(
            "\n🔍 What job role are you looking for? (or type 'exit' to quit): "
        ).strip()
        if job_role.lower() == "exit":
            print(
                "\n👋 Exiting AI Job Agent. Best of luck with your applications!"
            )
            break

        print(f"\n🌐 Scanning open listings for '{job_role}'...")
        jobs = search_jobs(job_role)

        if not jobs:
            print("❌ No matching job listings found for this role.")
            continue

        scored_jobs = []
        for job in jobs:
            job_skills = job.get("skills", [])
            matched = [s for s in candidate_skills if s in job_skills]
            missing = [s for s in job_skills if s not in candidate_skills]
            score = (len(matched) / len(job_skills)) * 100 if job_skills else 0

            scored_jobs.append({
                "title": job.get("title"),
                "company": job.get("company"),
                "url": job.get("url"),
                "score": round(score, 2),
                "matched": matched,
                "missing": missing,
            })

        scored_jobs.sort(key=lambda x: x["score"], reverse=True)

        job_index = 0
        while job_index < len(scored_jobs):
            job = scored_jobs[job_index]
            print("\n" + "=" * 50)
            print(
                f"🎯 MATCH OPTION [{job_index + 1}/{len(scored_jobs)}]:"
            )
            print(f"📌 Job Title      : {job['title']}")
            print(f"🏢 Company        : {job['company']}")
            print(f"📊 Match Score    : {job['score']}%")
            print(
                f"✅ Matching Skills: {', '.join(job['matched']) if job['matched'] else 'None'}"
            )
            print(
                f"⚠️ Missing Skills : {', '.join(job['missing']) if job['missing'] else 'None'}"
            )
            print(f"🔗 Portal Link    : {job['url']}")
            print("=" * 50)

            user_action = (
                input(
                    "\n👉 Would you like to apply for this job? [y = Apply, n = Next Job, s = Search Another Role]: "
                )
                .strip()
                .lower()
            )

            if user_action == "y":
                auto_fill_job_application(job["url"], candidate_profile)
                job_index += 1
            elif user_action == "n":
                job_index += 1
                if job_index >= len(scored_jobs):
                    print(
                        f"\n⚠️ All matches for '{job_role}' have been reviewed. Let's try searching for another role!"
                    )
            elif user_action == "s":
                break
            else:
                print("⚠️ Invalid choice. Please enter 'y', 'n', or 's'.")


if __name__ == "__main__":
    main()