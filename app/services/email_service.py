import os
import httpx
from dotenv import load_dotenv

load_dotenv(override=True)

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")

SENDGRID_API_URL = "https://api.sendgrid.com/v3/mail/send"


async def send_otp_email(email: str, otp: str):
    headers = {
        "Authorization": f"Bearer {SENDGRID_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "personalizations": [
            {"to": [{"email": email}], "subject": "Your OTP Code for Verification"}
        ],
        "from": {"email": SENDER_EMAIL},
        "content": [
            {
                "type": "text/plain",
                "value": f"Your OTP code is: {otp}. It is valid for 10 minutes.",
            }
        ],
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                SENDGRID_API_URL, headers=headers, json=payload
            )
            response.raise_for_status()
            print(f"Email sent to {email}. Status Code: {response.status_code}")
        except httpx.HTTPStatusError as e:
            print(f"Failed to send OTP email: {e.response.text}")
        except Exception as e:
            print(f"Error sending OTP email: {e}")
