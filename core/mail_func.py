import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config.settings import settings


def send_mail(email: str, otp: str):
    msg = MIMEMultipart()
    msg["From"] = settings.EMAIL_FROM
    msg["To"] = email
    msg["Subject"] = "OTP Verification"
    msg.attach(
        MIMEText(
            f"Your OTP is {otp}. It expires in 5 minutes.",
            "plain"
        )
    )

    cfg = settings.EMAIL_CONFIGS[settings.EMAIL_PROVIDER]
    server = smtplib.SMTP(cfg["host"], cfg["port"])
    server.starttls()
    server.login(settings.EMAIL_USERNAME, settings.EMAIL_PASSWORD)
    server.send_message(msg)
    server.quit()
