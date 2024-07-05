from django.core.exceptions import ValidationError


def validate_pin(pin: str):
    if len(pin) < 4:
        raise ValidationError("Pin must be four digit")


def validate_amount(amount: str):
    if len(amount) < 1:
        raise ValidationError("Can not deposit negative amount")
