import asyncio
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, status , BackgroundTasks
from starlette.requests import Request
from starlette.responses import JSONResponse
from werkzeug.security import check_password_hash

from config.settings import settings
from core.extensions import limiter
from core.db import otps, add_otp, get_otp, update_failed_attempts, update_verified, total_otp, verified_otp
from core.mail_func import send_mail
from core.token_auth import require_token
from models.models import VerifyOTP, SendOTP
from utils.otp_utlis import generate_otp

app_router = APIRouter()


@app_router.get("/")
def health():
    return {"status": "Active"}


@app_router.post("/send-otp")
@limiter.limit("25/minute")
async def send_otp(background_tasks: BackgroundTasks, data: SendOTP, request: Request, token_check=Depends(require_token)):
    otp = generate_otp()
    added = await add_otp(str(data.email), otp)
    if not added:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="An OTP already exists for this email address"
        )

    background_tasks.add_task(send_mail, str(data.email), otp)
    return JSONResponse(status_code=202, content={"message": "OTP sent"})


@app_router.post("/verify-otp")
@limiter.limit("50/minute")
async def verify_otp(data: VerifyOTP, request: Request, token_check=Depends(require_token)):
    record = await get_otp(str(data.email))

    if not record:
        raise HTTPException(status_code=400, detail="OTP not found")

    created_at = record["created_at"]

    if datetime.now(timezone.utc) - created_at > timedelta(minutes=settings.EXPIRE_TIME):
        await otps.delete_one({"email": str(data.email)})
        raise HTTPException(status_code=400, detail="OTP expired")

    if record["verified"]:
        raise HTTPException(status_code=400, detail="OTP already verified")

    if record["failed_attempts"] >= 3:
        raise HTTPException(status_code=400, detail="Too many failed attempts")

    if not check_password_hash(record["otp"], data.otp):
        await update_failed_attempts(str(data.email))
        raise HTTPException(status_code=400, detail="Invalid OTP")

    await update_verified(str(data.email))
    return JSONResponse(status_code=200, content={"message": "OTP verified"})


@app_router.get("/otp-stats")
async def stats(token_check=Depends(require_token)):
    return {
        "total": await total_otp(),
        "verified": await verified_otp()
    }