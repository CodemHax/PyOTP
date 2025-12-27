# 🏰 PyOTP Vault
A simple, secure, and self-hostable email OTP verification system built with FastAPI (ported from Flask).

## ✨ Features
- 🔐 Secure 6-digit OTP generation and verification with input validation
- 📧 Email delivery via any SMTP (Gmail, Outlook, custom)
- ⏰ OTP expiry (default: 5 minutes)
- 🗄️ MongoDB storage for OTPs and stats
- 📊 Built-in usage statistics endpoint
- 🛡️ API token authentication for all endpoints
- 🚦 Rate limiting to prevent abuse (7/min for send, 5/min for verify)
- 🔒 Failed attempt lockout (3 attempts max)
- 📝 Comprehensive logging for security events
- 🛡️ Security headers (HSTS, X-Frame-Options, etc.)
- ✅ Email and OTP format validation
- 🐳 Easy Docker deployment
- 📝 Simple test script included

## 🚀 Quick Start
**Requirements:** Python 3.7+, MongoDB, Email account (with SMTP access)

## Installation & Setup

1. **Clone and install dependencies:**
   ```bash
   git clone https://github.com/CodemHax/PyOTP
   cd PyOTP
   pip install -r requirements.txt
   ```

2. **Configure `.env` file:**
   ```env
   MONGO_URI=mongodb://localhost:27017/otp-verification  # Default: mongodb://localhost:27017/
   EMAIL_USERNAME=your-email@gmail.com
   EMAIL_PASSWORD=your-app-password  # For Gmail, use an App Password
   API_TOKEN=your-secure-api-token
   EMAIL_FROM=your-email@gmail.com
   PORT=7000  # Default port
   OTP_EXPIRY=5  # Optional, in minutes
   ```

   - For Gmail, enable 2FA and create an App Password (Google Account > Security > App passwords)

3. **Start MongoDB** (locally or with Docker)

4. **Run the server:**
   ```bash
   python main.py
   ```

## 📡 API Usage
All endpoints require header: `X-API-Token: YOUR_TOKEN`

### Send OTP
- **POST /send-otp**
- Body: `{ "email": "user@example.com" }`
- Sends a one-time code to the email address.

### Verify OTP
- **POST /verify-otp**
- Body: `{ "email": "user@example.com", "otp": "123456" }`
- Verifies the OTP for the email address.

### Get Stats
- **GET /otp-stats**
- Returns usage statistics (total OTPs and verified count).

## 🧪 Testing
Run the included test script:
```bash
python test.py
```

## 🐳 Docker
```bash
docker-compose up -d
```

## 📄 License
MIT License - Feel free to use and modify!

## 📋 Changelog
### v1.1.0 - Security Enhancements (December 2025)
- 🔐 Increased OTP length to 6 digits for better security
- 🚦 Added rate limiting to verify-otp endpoint (5/min)
- 🔒 Implemented failed attempt tracking and lockout after 3 failures
- 📝 Added comprehensive logging for security events and unauthorized access
- 🛡️ Integrated security headers middleware (HSTS, X-Frame-Options, etc.)
- ✅ Enhanced input validation for email and OTP formats
- ⏰ Fixed datetime handling to use timezone-aware objects
- 🔄 Ported from Flask to FastAPI for improved performance and features
