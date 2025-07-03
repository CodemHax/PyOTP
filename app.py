from flask import Flask, request, jsonify
from dataclasses import dataclass
import random
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import os
import logging
import smtplib
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

load_dotenv()
app = Flask(__name__)

# MongoDB configuration
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client.otp_database
otp_collection = db.otps

EMAIL_CONFIGS = {
    "gmail": {"host": "smtp.gmail.com", "port": 587},
}

EMAIL_PROVIDER = "gmail"
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
API_TOKEN = os.getenv("API_TOKEN")

logging.basicConfig(level=logging.INFO)

# Initialize Flask-Limiter with MongoDB as the storage backend
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=MONGO_URI,
    default_limits=["10 per minute"]
)
limiter.init_app(app)

@dataclass
class EmailRequest:
    email: str

@dataclass
class OTPVerification:
    email: str
    otp: str

def token_required(f):
    def decorator(*args, **kwargs):
        token = request.headers.get('X-API-Token')
        if not token or token != API_TOKEN:
            return jsonify({"detail": "Invalid or missing API token"}), 403
        return f(*args, **kwargs)
    return decorator

def generate_otp():
    return "".join([str(random.randint(0, 9)) for _ in range(4)])

def send_email(to_email: str, otp: str):
    try:
        if not EMAIL_USERNAME or not EMAIL_PASSWORD:
            logging.error("Email credentials are not set")
            return False

        msg = MIMEMultipart()
        msg["From"] = EMAIL_USERNAME
        msg["To"] = to_email
        msg["Subject"] = "Your OTP for Verification"
        body = f"""
        Your OTP is: {otp}
        This OTP will expire in 5 minutes.
        Please do not share this OTP with anyone.
        """
        msg.attach(MIMEText(body, "plain"))

        server_config = EMAIL_CONFIGS[EMAIL_PROVIDER]

        server = smtplib.SMTP(server_config["host"], server_config["port"])
        server.starttls()
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        logging.error(f"Error sending email: {e}")
        return False

@app.route("/", methods=["GET"], endpoint="check_alive")
def check_alive():
    return jsonify({"message": "Server is running"})

@app.route("/send-otp", methods=["POST"], endpoint="send_otp")
@token_required
@limiter.limit("7 per minute")
def send_otp():
    data = request.get_json()
    email_request = EmailRequest(**data)
    otp = generate_otp()
    hashed_otp = generate_password_hash(otp)
    if send_email(email_request.email, otp):
        otp_collection.update_one(
            {"email": email_request.email},
            {
                "$set": {
                    "otp": hashed_otp,
                    "created_at": datetime.now(),
                    "verified": False
                }
            },
            upsert=True
        )
        return jsonify({"message": "OTP sent successfully"})
    return jsonify({"detail": "Failed to send OTP"}), 500

@app.route("/verify-otp", methods=["POST"], endpoint="verify_otp")
@token_required
def verify_otp():
    data = request.get_json()
    otp_verification = OTPVerification(**data)
    otp_record = otp_collection.find_one({"email": otp_verification.email})

    if not otp_record:
        return jsonify({"detail": "No OTP found for this email"}), 400

    if datetime.now() - otp_record["created_at"] > timedelta(minutes=5):
        otp_collection.delete_one({"email": otp_verification.email})
        return jsonify({"detail": "OTP expired"}), 400

    if not check_password_hash(otp_record["otp"], otp_verification.otp):
        return jsonify({"detail": "Invalid OTP"}), 400

    if otp_record["verified"]:
        return jsonify({"detail": "OTP already used"}), 400

    otp_collection.update_one(
        {"email": otp_verification.email},
        {"$set": {"verified": True}}
    )
    return jsonify({"message": "OTP verified successfully"}), 200

@app.route("/otp-stats", methods=["GET"], endpoint="otp_stats")
@token_required
def otp_stats():
    total_otps = otp_collection.count_documents({})
    verified_otps = otp_collection.count_documents({"verified": True})
    return jsonify({
        "total_otps": total_otps,
        "verified_otps": verified_otps
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
