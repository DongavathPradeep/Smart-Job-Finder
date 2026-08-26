import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "dungavathpradeepnaik123@gmail.com"
# కింద ఉన్న దాంట్లో మీ 16 అక్షరాల Google App Password మాత్రమే పెట్టండి (స్పేస్‌లు లేకుండా)
SENDER_APP_PASSWORD = "ezbbfkpvualdmlur" 

def send_email_alert(recipient_email: str, candidate_name: str, matched_jobs: list):
    if not matched_jobs:
        return False, "No jobs available to send."

    # Filter top matching jobs
    top_jobs = [j for j in matched_jobs if j.get("semantic_score", 0) >= 50][:5]
    if not top_jobs:
        top_jobs = matched_jobs[:3]

    subject = f"⚡ Smart Job Finder: Top Matched Roles for {candidate_name}"

    body_html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #1e293b; line-height: 1.6;">
        <h2 style="color: #0284c7;">⚡ Smart Job Finder Digest</h2>
        <p>Hello <b>{candidate_name}</b>,</p>
        <p>Here are your top semantic matched job openings:</p>
        <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
            <thead>
                <tr style="background: #0f172a; color: #38bdf8; text-align: left;">
                    <th style="padding: 10px; border: 1px solid #334155;">Role</th>
                    <th style="padding: 10px; border: 1px solid #334155;">Company</th>
                    <th style="padding: 10px; border: 1px solid #334155;">Match Score</th>
                    <th style="padding: 10px; border: 1px solid #334155;">Action</th>
                </tr>
            </thead>
            <tbody>
    """

    for job in top_jobs:
        body_html += f"""
                <tr>
                    <td style="padding: 10px; border: 1px solid #cbd5e1;"><b>{job.get('title')}</b></td>
                    <td style="padding: 10px; border: 1px solid #cbd5e1;">{job.get('company')}</td>
                    <td style="padding: 10px; border: 1px solid #cbd5e1; color: #10b981; font-weight: bold;">{job.get('semantic_score')}%</td>
                    <td style="padding: 10px; border: 1px solid #cbd5e1;"><a href="{job.get('url', '#')}" style="color: #0284c7; font-weight: 600;">Apply Now</a></td>
                </tr>
        """

    body_html += """
            </tbody>
        </table>
        <br>
        <p style="font-size: 0.82rem; color: #64748b;">Automated by Smart Job Finder • Engineered by Dongavath Pradeep</p>
    </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = recipient_email
    msg.attach(MIMEText(body_html, "html"))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=15)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
        server.sendmail(SENDER_EMAIL, recipient_email, msg.as_string())
        server.quit()
        return True, "Email sent successfully!"
    except Exception as e:
        return False, str(e)
