import requests

BASE_URL = "http://127.0.0.1:7000"
API_TOKEN = "qw3638d8ebe8vfvdjbueveieviei"

def test_send_otp(email):
    headers = {"X-API-Token": API_TOKEN}
    response = requests.post(f"{BASE_URL}/send-otp", json={"email": email}, headers=headers)
    print("Send OTP Response:", response.json())
    return response

def test_verify_otp(email, otp):
    headers = {"X-API-Token": API_TOKEN}
    response = requests.post(f"{BASE_URL}/verify-otp", json={"email": email, "otp": otp}, headers=headers)
    print("OTP Verification Response:", response.status_code)
    print("Verify OTP Response:", response.json())
    return response

if __name__ == "__main__":
    test_email = input("Enter the email address: ")
    print("Sending OTP to", test_email)
    send_response = test_send_otp(str(test_email))
    if send_response.status_code == 202:
        otp = input("Enter the OTP received in the email: ")
        test_verify_otp(test_email, otp)
    else:
        print("Failed to send OTP")