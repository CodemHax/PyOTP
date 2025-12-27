import uvicorn
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from werkzeug.security import generate_password_hash, check_password_hash
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import smtplib
import random
import os
from starlette.middleware.base import BaseHTTPMiddleware
import asyncio

load_dotenv()

app = FastAPI()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
API_TOKEN = os.getenv("API_TOKEN")
EMAIL_FROM = os.getenv("EMAIL_FROM")

EMAIL_PROVIDER = "smtp2go"
EMAIL_CONFIGS = {
    "smtp2go": {"host": "mail.smtp2go.com", "port": 2525}
}

client = AsyncIOMotorClient(MONGO_URI)
db = client.otp_database
otps = db.otps

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(status_code=429, content={"detail": "Too many requests"})

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

app.add_middleware(SecurityHeadersMiddleware)

class SendOTP(BaseModel):
    email: EmailStr

class VerifyOTP(BaseModel):
    email: EmailStr
    otp: str

def require_token(request: Request):
    token = request.headers.get("X-API-Token")
    if token != API_TOKEN:
        raise HTTPException(status_code=403, detail="Unauthorized")

def generate_otp():
    return "".join(str(random.randint(0, 9)) for i in range(6))

def send_mail(email: str, otp: str):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_FROM
    msg["To"] = email
    msg["Subject"] = "OTP Verification"
    msg.attach(
        MIMEText(f"Your OTP is {otp}. It expires in 5 minutes.", "plain")
    )

    cfg = EMAIL_CONFIGS[EMAIL_PROVIDER]
    server = smtplib.SMTP(cfg["host"], cfg["port"])
    server.starttls()
    server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
    server.send_message(msg)
    server.quit()


@app.get("/")
def health():
    return {"status": "ok"}

@app.post("/send_otp")
@limiter.limit("25/minute")
async def send_otp(data: SendOTP, request: Request, token_check=Depends(require_token)):
    otp = generate_otp()

    await otps.update_one(
        {"email": data.email},
        {
            "$set": {
                "otp": generate_password_hash(otp),
                "created_at": datetime.now(timezone.utc),
                "verified": False,
                "failed_attempts": 0
            }
        },
        upsert=True
    )

    await asyncio.to_thread(send_mail, data.email, otp)
    return JSONResponse(status_code=202, content={"message": "OTP sent"})

@app.post("/verify_otp")
@limiter.limit("50/minute")
async def verify_otp(data: VerifyOTP, request: Request, token_check=Depends(require_token)):
    record = await otps.find_one({"email": data.email})

    if not record:
        raise HTTPException(status_code=400, detail="OTP not found")

    if datetime.now(timezone.utc) - record["created_at"] > timedelta(minutes=5):
        await otps.delete_one({"email": data.email})
        raise HTTPException(status_code=400, detail="OTP expired")

    if record["verified"]:
        raise HTTPException(status_code=400, detail="OTP already used")

    if record.get("failed_attempts", 0) >= 3:
        raise HTTPException(status_code=400, detail="Too many failed attempts")

    if not check_password_hash(record["otp"], data.otp):
        await otps.update_one(
            {"email": data.email},
            {"$inc": {"failed_attempts": 1}}
        )
        raise HTTPException(status_code=400, detail="Invalid OTP")

    await otps.update_one(
        {"email": data.email},
        {"$set": {"verified": True}}
    )

    return JSONResponse(status_code=200, content={"message": "OTP verified"})

@app.get("/otp_stats")
async def stats(token_check=Depends(require_token)):
    return {
        "total": await otps.count_documents({}),
        "verified": await otps.count_documents({"verified": True})
    }

