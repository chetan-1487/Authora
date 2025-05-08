import random, string
import re

def generate_otp() -> str:
    return ''.join(random.choices(string.digits, k=6))


def is_password_strong(password: str) -> bool:
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'\d', password):
        return False
    if not re.search(r'[@$!%*?&]', password):
        return False
    return True
