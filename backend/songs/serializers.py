from backend.core.serializers import CharField, IntegerField, Serializer
from backend.database import ALLOWED_GENRES


class SongCreateSerializer(Serializer):
    fields = {
        "artist_id": IntegerField(),
        "title": CharField(max_length=255),
        "album_name": CharField(
            max_length=255,
            required=False,
            blank=True,
            null=True,
        ),
        "genre": CharField(
            max_length=64,
            choices=ALLOWED_GENRES,
        ),
    }


class SongUpdateSerializer(Serializer):
    fields = {
        "id": IntegerField(),
        "artist_id": IntegerField(required=False, null=True),
        "title": CharField(max_length=255, required=False, null=True),
        "album_name": CharField(
            max_length=255,
            required=False,
            blank=True,
            null=True,
        ),
        "genre": CharField(
            max_length=64,
            required=False,
            null=True,
            choices=ALLOWED_GENRES,
        ),
    }
