import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import streamlit as st

def send_email_alert(recipient_email: str, candidate_name: str, matched_jobs: list) -> bool:
    """
    Dispatches styled HTML email alert with matched tech roles.
    Reads credentials from Streamlit Secrets or Environment Variables.
    """
    # Check Streamlit Secrets first, then fallback to OS Environment variables
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    
    sender_email = None
    sender_password = None

    if hasattr(st, "secrets") and "SMTP_EMAIL" in st.secrets:
        sender_email = st.secrets.get("SMTP_EMAIL")
        sender_password = st.secrets.get("SMTP_PASSWORD")
    else:
        sender_email = os.getenv("SMTP_EMAIL", "test@gmail.com")
        sender_password = os.getenv("SMTP_PASSWORD", "")

    if not sender_password or not recipient_email:
        # Graceful simulation if credentials are not configured yet
        st.info(f"📧 [Preview Mode] Email payload prepared for {recipient_email} with {len(matched_jobs)} job matches.")
        return True

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"JobNexus Career Alert: {len(matched_jobs)} High-Fit Opportunities"
        msg["From"] = f"JobNexus Intelligence <{sender_email}>"
        msg["To"] = recipient_email

        job_rows = ""
        for job in matched_jobs[:8]:
            title = job.get("title", "Role Opening")
            company = job.get("company", "Tech Enterprise")
            score = job.get("match_score", "80")
            url = job.get("url", "#")
            job_rows += f"""
            <tr style="border-bottom: 1px solid #e2e8f0;">
                <td style="padding: 10px; font-weight: 600; color: #1e293b;">{title}</td>
                <td style="padding: 10px; color: #64748b;">{company}</td>
                <td style="padding: 10px; color: #10b981; font-weight: 700;">{score}%</td>
                <td style="padding: 10px;"><a href="{url}" style="color: #2563eb; text-decoration: none; font-weight: 600;">Apply &rarr;</a></td>
            </tr>
            """

        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f8fafc; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: #ffffff; padding: 20px; border-radius: 8px; border: 1px solid #e2e8f0;">
                <h2 style="color: #0f172a; margin-top: 0;">JobNexus Career Digest</h2>
                <p style="color: #475569;">Hello <b>{candidate_name}</b>,</p>
                <p style="color: #475569;">Here are your highest-matched live engineering roles based on your latest skill scan:</p>
                <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
                    <thead>
                        <tr style="background: #f1f5f9; text-align: left;">
                            <th style="padding: 8px;">Role</th>
                            <th style="padding: 8px;">Company</th>
                            <th style="padding: 8px;">Match</th>
                            <th style="padding: 8px;">Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {job_rows}
                    </tbody>
                </table>
                <br>
                <p style="font-size: 0.8rem; color: #94a3b8; text-align: center;">Sent via JobNexus Automated Career Engine</p>
            </div>
        </body>
        </html>
        """

        msg.attach(MIMEText(html_body, "html"))

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"SMTP Dispatch Error: {str(e)}")
        return False
