import random
import string

# OTP Generator
def generate_otp() -> str:
    return "".join(random.choices(string.digits, k=6))
