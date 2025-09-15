from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.user_mgt import router as user_mngt_router
from routers.bookings import router as bookings_router
from routers.contact import router as contact_router
from routers.reviews import router as reviews_router
from fastapi.staticfiles import StaticFiles
import os


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_mngt_router)
app.include_router(bookings_router)
app.include_router(contact_router)
app.include_router(reviews_router)

uploads_path = os.path.join(os.path.dirname(__file__), "Files")
app.mount("/Files", StaticFiles(directory=uploads_path), name="Files")


@app.get("/")
async def root():
    return {"message": "Welcome to the YPA Mbuzi Choma Backend!"}
