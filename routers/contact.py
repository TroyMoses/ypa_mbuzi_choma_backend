from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session

from database import get_db
from models import Contact
from routers.schemas import ContactCreate, ContactResponse
from utils.email_utils import send_email, ADMIN_EMAIL

router = APIRouter(prefix="/contact", tags=["contact"])


@router.post("", response_model=ContactResponse)
def submit_contact(request: ContactCreate, db: Session = Depends(get_db)):
    new_contact = Contact(
        name=request.name,
        email=request.email,
        phone=request.phone,
        subject=request.subject,
        message=request.message,
    )
    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)

    # Send confirmation email to customer
    customer_subject = "We Received Your Message - YPA Mbuzi Choma"
    customer_body = f"""
Hi {new_contact.name},

Thank you for contacting YPA Mbuzi Choma! 
We have received your message regarding "{new_contact.subject}" and will get back to you within 24 hours.

Message you sent:
{new_contact.message}

Best regards,
YPA Mbuzi Choma Team
"""
    send_email(new_contact.email, customer_subject, customer_body)

    # Notify admin
    admin_subject = "New Contact Form Submission"
    admin_body = f"""
New contact form submitted:

Name: {new_contact.name}
Email: {new_contact.email}
Phone: {new_contact.phone or "N/A"}
Subject: {new_contact.subject}
Message: {new_contact.message}
"""
    send_email(ADMIN_EMAIL, admin_subject, admin_body)

    return new_contact



@router.get("", response_model=list[ContactResponse])
def list_contacts(
    db: Session = Depends(get_db),
    token: str = Header(...),
    role: str = Header(...),
    is_admin: str = Header(...),
):
    if is_admin.lower() != "true":
        raise HTTPException(status_code=403, detail="Admins only")
    return db.query(Contact).order_by(Contact.created_at.desc()).all()
