from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from werkzeug.security import generate_password_hash
from config.settings import settings


client = AsyncIOMotorClient(settings.MONGO_URI, tz_aware=True, tzinfo=timezone.utc)
db = client.otp_database
otps = db.otps


async def add_otp(email: str, otp: str):
    try:
        done = await otps.update_one(
            {"email": email},
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
        return done.acknowledged
    except Exception as e:
        print(e)
        return False


async def get_otp(email: str) -> dict | None:
    record = await otps.find_one({"email": email})
    return record

async def update_failed_attempts(email: str):
    done = await otps.update_one({"email": email}, {"$inc": {"failed_attempts": 1}})
    return done

async def delete_otp(email: str):
    done = await otps.delete_one({"email": email})
    return done

async def update_verified(email: str):
    done = await otps.update_one({"email": email}, {"$set": {"verified": True}})
    return done

async def total_otp():
    return await otps.count_documents({})

async def verified_otp():
    return await otps.count_documents({"verified": True})


