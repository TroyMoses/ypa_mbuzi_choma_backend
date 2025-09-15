from pydantic import BaseModel, EmailStr
from typing import List, Optional
from enum import Enum
from datetime import date, datetime

## ======================
## AUTH SCHEMAS
## ======================


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginUser(BaseModel):
    id: int
    username: str
    role: str
    is_admin: bool

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    token: str
    user: LoginUser


class VerifyResponse(BaseModel):
    id: int
    username: str
    role: str
    is_admin: bool

    class Config:
        from_attributes = True


## ======================
## EXISTING USER SCHEMAS
## ======================


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str


class ResetPasswordRequest(BaseModel):
    email: EmailStr


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str

    class Config:
        from_attributes = True


## ======================
## BOOKING SCHEMAS
## ======================
class BookingCreate(BaseModel):
    customer_name: str
    customer_email: EmailStr
    customer_phone: str
    booking_date: date
    booking_time: str
    party_size: int
    special_requests: str | None = None


class BookingResponse(BaseModel):
    id: int
    customer_name: str
    customer_email: EmailStr
    customer_phone: str
    booking_date: date
    booking_time: str
    party_size: int
    special_requests: str | None
    created_at: datetime

    class Config:
        from_attributes = True


## ======================
## CONTACT SCHEMAS
## ======================
class ContactCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str | None = None
    subject: str
    message: str


class ContactResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: str | None
    subject: str
    message: str
    created_at: datetime

    class Config:
        from_attributes = True


## ======================
## REVIEW SCHEMAS
## ======================
class ReviewCreate(BaseModel):
    customer_name: str
    customer_email: EmailStr
    rating: int
    comment: str
    menu_id: int


class ReviewResponse(BaseModel):
    id: int
    customer_name: str
    customer_email: EmailStr
    rating: int
    comment: str | None
    menu_id: int
    created_at: datetime

    class Config:
        from_attributes = True


