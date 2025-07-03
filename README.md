# 🏰 PyOTP Vault

A simple, secure, and self-hostable email OTP verification system built with Python.

## ✨ Features

- 🔐 Secure 6-digit OTP generation and verification
- 📧 Email delivery via any SMTP (Gmail, Outlook, custom)
- ⏰ OTP expiry (default: 5 minutes)
- 🗄️ MongoDB storage for OTPs and stats
- 📊 Built-in usage statistics endpoint
- 🛡️ API token authentication for all endpoints
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
   MONGO_URI=mongodb://localhost:27017/otp-verification
   EMAIL_USERNAME=your-email@gmail.com
   EMAIL_PASSWORD=your-app-password  # For Gmail, use an App Password
   API_TOKEN=your-secure-api-token
   PORT=5000  # Optional, default is 3000
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
- **GET /top-sats**
- Returns usage statistics (e.g., most active emails).

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
