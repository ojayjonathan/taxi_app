import re


def emailValidator(email):
    return re.match(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', email)


def phone_number_validator(phone_number):
    return re.match(r"\+254\w{9}", phone_number)
