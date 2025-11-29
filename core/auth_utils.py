import re

username_pattern = re.compile(r"^[a-zA-Z0-9_]{4,32}$")
email_pattern = re.compile(r"^[^@\s]+@[^@\s]+\.[a-zA-Z0-9]+$")


def validate_username(username):
    return bool(username_pattern.match(username))

def validate_email(email):
    return bool(email_pattern.match(email))
    