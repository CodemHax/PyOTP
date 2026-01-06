# PyOTP Microservice

A Python microservice for generating and verifying One-Time Passwords (OTP), with built-in rate limiting, token authentication, and email support. Easily integrable into larger systems for secure authentication workflows.

## Features

### Core Functionality
- **OTP Generation**: Generate secure 6-digit OTPs with configurable expiration time (default: 5 minutes)
- **OTP Verification**: Verify OTPs with built-in security measures
- **Email Delivery**: Send OTPs via email with background task processing
- **Multiple Email Providers**: Support for Gmail, Outlook, Yahoo, and custom SMTP servers

### Security Features
- **Token-Based Authentication**: API token authentication via `X-API-Token` header
- **Rate Limiting**: 
  - 25 requests/minute for OTP sending
  - 50 requests/minute for OTP verification
- **Failed Attempt Protection**: Maximum 3 failed verification attempts per OTP
- **OTP Expiration**: Automatic expiration after configured time
- **Password Hashing**: OTPs stored as hashed values using Werkzeug security
- **Security Headers**: 
  - X-Content-Type-Options: nosniff
  - X-Frame-Options: DENY
  - X-XSS-Protection
  - Strict-Transport-Security (HSTS)

### Database & Storage
- **MongoDB Integration**: Async MongoDB operations using Motor
- **OTP Tracking**: Track total and verified OTPs
- **Automatic Cleanup**: Expired OTPs are automatically removed

### API Endpoints
- `GET /`: Health check endpoint
- `POST /send-otp`: Send OTP to email address
- `POST /verify-otp`: Verify OTP for email address
- `GET /otp-stats`: Get statistics (total and verified OTPs)

### Architecture
- **FastAPI Framework**: High-performance async API
- **Modular Design**: Separated routes, models, core logic, and utilities
- **Scalable**: Designed for microservice architecture
- **Background Tasks**: Non-blocking email sending
- **Docker Support**: Dockerfile included for containerization
- **Vercel Deployment**: Ready for serverless deployment

## Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/OTPv4.git
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

## Usage

### Running the Microservice
1. Configure your `.env` file (see Configuration section)
2. Run the microservice:
   ```sh
   python app.py
   ```
   The service will start on `http://localhost:7000`

### API Examples

#### Health Check
```sh
curl http://localhost:7000/
```

#### Send OTP
```sh
curl -X POST http://localhost:7000/send-otp \
  -H "Content-Type: application/json" \
  -H "X-API-Token: your_api_token" \
  -d '{"email": "user@example.com"}'
```

#### Verify OTP
```sh
curl -X POST http://localhost:7000/verify-otp \
  -H "Content-Type: application/json" \
  -H "X-API-Token: your_api_token" \
  -d '{"email": "user@example.com", "otp": "123456"}'
```

#### Get Statistics
```sh
curl http://localhost:7000/otp-stats \
  -H "X-API-Token: your_api_token"
```

## Project Structure
```
app.py                # Microservice entry point
config/settings.py    # Configuration settings
core/                 # Core logic (DB, mail, rate limit, auth)
models/models.py      # Database models
routes/main_routes.py # API routes
utils/otp_utlis.py    # OTP utility functions
```

## Configuration
Edit `config/settings.py` to set up environment variables, email credentials, and other options.

### Environment Variables
Create a `.env` file in the root directory with the following variables:
```env
API_TOKEN=your_secure_api_token
MONGO_URI=your_mongodb_connection_string
EMAIL_PROVIDER=gmail  # or outlook, yahoo, custom
EMAIL_USERNAME=your_email@example.com
EMAIL_PASSWORD=your_email_password
EMAIL_FROM=your_email@example.com
EXPIRE_TIME=5  # OTP expiration time in minutes
```

## Testing
Run tests using:
```sh
python test.py
```

## License
This project is licensed under the terms of the LICENSE file.
