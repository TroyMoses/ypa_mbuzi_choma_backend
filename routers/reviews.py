from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session

from database import get_db
from models import Review
from routers.schemas import ReviewCreate, ReviewResponse
from utils.email_utils import send_email, ADMIN_EMAIL

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("", response_model=ReviewResponse)
def submit_review(request: ReviewCreate, db: Session = Depends(get_db)):
    new_review = Review(
        customer_name=request.customer_name,
        customer_email=request.customer_email,
        rating=request.rating,
        comment=request.comment,
        menu_id=request.menu_id,
    )
    db.add(new_review)
    db.commit()
    db.refresh(new_review)

    # Send confirmation email to customer
    customer_subject = "Thank You for Your Review - YPA Mbuzi Choma"
    customer_body = f"""
Hi {new_review.customer_name},

Thank you for your review! We appreciate your feedback and are glad you shared your experience.

Your Review:
Rating: {new_review.rating}/5
Comment: {new_review.comment or "No comment"}

Best regards,
YPA Mbuzi Choma Team
"""
    send_email(new_review.customer_email, customer_subject, customer_body)

    # Notify admin
    admin_subject = "New Customer Review"
    admin_body = f"""
New review submitted:

Name: {new_review.customer_name}
Email: {new_review.customer_email}
Rating: {new_review.rating}/5
Comment: {new_review.comment or "No comment"}
"""
    send_email(ADMIN_EMAIL, admin_subject, admin_body)

    return new_review



@router.get("", response_model=list[ReviewResponse])
def list_reviews(
    db: Session = Depends(get_db),
    token: str = Header(...),
    role: str = Header(...),
    is_admin: str = Header(...),
):
    if is_admin.lower() != "true":
        raise HTTPException(status_code=403, detail="Admins only")
    return db.query(Review).order_by(Review.created_at.desc()).all()
