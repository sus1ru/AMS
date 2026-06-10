from datetime import datetime, UTC

from backend.core.exceptions import FieldValidationError
from backend.core.serializers import CharField, DateTimeField, EmailField, Serializer
from backend.database import ALLOWED_ROLES, ALLOWED_GENDERS

def dob_not_in_future(value):
    today = datetime.now(UTC).date()
    datetime_dob = datetime.strptime(value, '%Y-%m-%d').astimezone(UTC).date()
    if datetime_dob > today:
        raise FieldValidationError("Field cannot be in the future")

class UserRegisterSerializer(Serializer):
    fields = {
        "first_name": CharField(max_length=255),
        "last_name": CharField(max_length=255),
        "email": EmailField(max_length=255),
        "password": CharField(max_length=500),
        "phone": CharField(
            max_length=20,
            required=False,
            blank=True,
            null=True,
        ),
        "dob": DateTimeField(
            required=False,
            blank=True,
            null=True,
            custom_validation=dob_not_in_future,
        ),
        "gender": CharField(
            max_length=4,
            required=False,
            blank=True,
            null=True,
            choices=ALLOWED_GENDERS,
        ),
        "address": CharField(
            max_length=255,
            required=False,
            blank=True,
            null=True,
        ),
        "role": CharField(
            max_length=64,
            choices=ALLOWED_ROLES,
        ),
    }


class UserLoginSerializer(Serializer):
    fields = {
        "email": EmailField(max_length=255),
        "password": CharField(max_length=500),
    }