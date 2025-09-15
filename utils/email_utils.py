import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@ypambuzi.com")
FROM_EMAIL = os.getenv("FROM_EMAIL", SMTP_USERNAME)


def send_email(to_email: str, subject: str, body: str):
    """Send an email via configured SMTP server."""
    msg = MIMEMultipart()
    msg["From"] = FROM_EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            print("ADMIN_EMAIL:", os.getenv("ADMIN_EMAIL"))
            print("FROM_EMAIL:", os.getenv("FROM_EMAIL"))

            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(FROM_EMAIL, to_email, msg.as_string())
    except Exception as e:
        print(f"❌ Error sending email to {to_email}: {e}")
