from datetime import datetime, UTC

from backend.auth.serializers import dob_not_in_future
from backend.core.exceptions import FieldValidationError
from backend.core.serializers import CharField, DateTimeField, IntegerField, Serializer
from backend.database import ALLOWED_GENDERS

def valid_year(value):
    today = datetime.now(UTC).year
    if value > today:
        raise FieldValidationError("Field cannot be in the future")
    elif value < 0:
        raise FieldValidationError("Field cannot be negative")

class ArtistCreateSerializer(Serializer):
    fields = {
        "user_id": IntegerField(required=False, null=True),
        "name": CharField(max_length=255),
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
        "address": CharField(max_length=255, required=False, blank=True, null=True),
        "first_release_year": IntegerField(
            required=False,
            null=True,
            custom_validation=valid_year,
        ),
        "no_of_albums_released": IntegerField(required=False, null=True),
    }


class ArtistUpdateSerializer(ArtistCreateSerializer):
    fields = {
        key: field for key, field in ArtistCreateSerializer.fields.items()
    }

    for field in fields.values():
        field.required = False