from datetime import datetime
import os
from typing import Annotated, Optional
from dotenv import load_dotenv
from pytz import timezone
from fastapi import HTTPException, Header, Depends, status
import jwt
from zoneinfo import ZoneInfo
from email.message import EmailMessage
import smtplib
from passlib.context import CryptContext
import pytz


nairobi_tz = ZoneInfo("Africa/Nairobi")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

load_dotenv()
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

nairobi_tz = pytz.timezone("Africa/Nairobi")


def nairobi_now() -> datetime:
    return datetime.now(nairobi_tz)


# format datetime to string "%d-%m-%Y %H:%M" from datetime object
def format_datetime(dt: datetime) -> str:
    if not isinstance(dt, datetime):
        raise ValueError("Input must be a datetime object")
    return dt.strftime("%d-%m-%Y %H:%M")


# Check if a user is internal based on email domain
def is_internal_user(email: str) -> bool:
    return email.lower().endswith("@gtp.renu.ac.ug")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def verify_token(token: Annotated[str, Header()]):
    try:
        # Decode the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = payload.get("user")

    return user


# Function to send email
def send_email(
    to_emails: list[str],
    subject: str,
    body: str,
    cc: list[str] = None,
    bcc: list[str] = None,
):
    sender_email = os.getenv("APP_EMAIL")
    app_password = os.getenv("APP_PASSWORD")

    msg = EmailMessage()
    msg["From"] = sender_email
    msg["To"] = ", ".join(to_emails)
    if cc:
        msg["Cc"] = ", ".join(cc)
    if bcc:
        msg["Bcc"] = ", ".join(bcc)
    msg["Subject"] = subject
    msg.set_content(body)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(sender_email, app_password)
            smtp.send_message(msg)
        return True
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to send email")


# Function to send OTP email
def send_otp_email(to_email: str, otp: str):
    subject = "Your OTP Code"
    body = f"""
    Hello,

    Your One-Time Password (OTP) is: {otp}
    It is valid for 10 minutes.

    If you did not request a password reset, please ignore this email.

    Regards,
    Careers Support Team
    """
    send_email(to_emails=[to_email], subject=subject, body=body)
    if not send_email:
        raise HTTPException(status_code=500, detail="Failed to send OTP email")
    return True


# --- Base dependency for all authenticated users ---
def get_current_user_for_records(token: str = Header(...)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user = payload.get("user")
        print("USER: ", user)
        if not user or user["role"] != "records" or not user["is_admin"]:
            raise HTTPException(status_code=403, detail="Records admin access required")
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


def require_records_admin(user=Depends(get_current_user_for_records)):
    if user["role"] != "records" or not user["is_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Records admin access required",
        )
    return user

def get_current_user_for_finance(token: str = Header(...)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user = payload.get("user")
        print("USER: ", user)
        if not user or user["role"] != "finance" or not user["is_admin"]:
            raise HTTPException(status_code=403, detail="Finance admin access required")
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

def require_finance_admin(user=Depends(get_current_user_for_finance)):
    if user["role"] != "finance" or not user["is_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Finance admin access required",
        )
    return user
