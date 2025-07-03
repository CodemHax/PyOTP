import requests

from main import otp_stats

BASE_URL = ""
API_TOKEN = ""

def top_sats():
    headers = {"X-API-Token": API_TOKEN}
    response = requests.get(f"{BASE_URL}/top-sats", headers=headers)
    print("Top Sats Response:", response.json())
    return response

def test_send_otp(email):
    headers = {"X-API-Token": API_TOKEN}
    response = requests.post(f"{BASE_URL}/send-otp", json={"email": email}, headers=headers)
    print("Send OTP Response:", response.json())
    return response

def test_verify_otp(email, otp):
    headers = {"X-API-Token": API_TOKEN}
    response = requests.post(f"{BASE_URL}/verify-otp", json={"email": email, "otp": otp}, headers=headers)
    print("Verify OTP Response:", response.json())
    return response

if __name__ == "__main__":
    test_email = "mail"

    # Test sending OTP
    send_response = test_send_otp(test_email)

    if send_response.status_code == 200:
        # Extract OTP from the response (for testing purposes, you might need to get the OTP from the email)
        otp = input("Enter the OTP received in the email: ")

        # Test verifying OTP
        test_verify_otp(test_email, otp)
    else:
        print("Failed to send OTP")
