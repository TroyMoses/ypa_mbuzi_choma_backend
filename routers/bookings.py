from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session

from database import get_db
from models import Booking
from routers.schemas import BookingCreate, BookingResponse
from utils.email_utils import send_email, ADMIN_EMAIL

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.post("", response_model=BookingResponse)
def create_booking(request: BookingCreate, db: Session = Depends(get_db)):
    new_booking = Booking(
        customer_name=request.customer_name,
        customer_email=request.customer_email,
        customer_phone=request.customer_phone,
        booking_date=request.booking_date,
        booking_time=request.booking_time,
        party_size=request.party_size,
        special_requests=request.special_requests,
    )
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)

    # Send confirmation email to customer
    customer_subject = "Your Booking Confirmation - YPA Mbuzi Choma"
    customer_body = f"""
Hi {new_booking.customer_name},

Thank you for your booking with YPA Mbuzi Choma!

Details:
- Date: {new_booking.booking_date}
- Time: {new_booking.booking_time}
- Party Size: {new_booking.party_size}

We will confirm your reservation within 2 hours during business hours.

Best regards,
YPA Mbuzi Choma Team
"""
    send_email(new_booking.customer_email, customer_subject, customer_body)

    # Notify admin
    admin_subject = "New Booking Received"
    admin_body = f"""
New booking submitted:

Name: {new_booking.customer_name}
Email: {new_booking.customer_email}
Phone: {new_booking.customer_phone}
Date: {new_booking.booking_date}
Time: {new_booking.booking_time}
Party Size: {new_booking.party_size}
Special Requests: {new_booking.special_requests or "None"}
"""
    send_email(ADMIN_EMAIL, admin_subject, admin_body)

    return new_booking




@router.get("", response_model=list[BookingResponse])
def list_bookings(
    db: Session = Depends(get_db),
    token: str = Header(...),
    role: str = Header(...),
    is_admin: str = Header(...),
):
    if is_admin.lower() != "true":
        raise HTTPException(status_code=403, detail="Admins only")
    return db.query(Booking).order_by(Booking.created_at.desc()).all()
