import re

from backend.core.exceptions import FieldValidationError


class Field:
    def __init__(
        self,
        required=True,
        choices=None,
        blank=False,
        null=False,
        custom_validation=None
    ):
        self.required = required
        self.choices = choices
        self.blank = blank
        self.null = null
        self.custom_validation = custom_validation

    def validate(self, value):
        if value is None:
            if self.required:
                raise FieldValidationError("Field is required")

            if self.null:
                return value
            else:
                raise FieldValidationError("Field may not be null")

        if value == "" and not self.blank:
            raise FieldValidationError("This field may not be blank")

        if self.choices and value not in self.choices:
            raise FieldValidationError("Invalid choice")

        if self.custom_validation:
            self.custom_validation(value)

        return value


class CharField(Field):
    def __init__(
        self,
        max_length,
        required=True,
        choices=None,
        blank=False,
        null=False,
        custom_validation=None
    ):
        super().__init__(
            required=required,
            choices=choices,
            blank=blank,
            null=null,
            custom_validation=custom_validation,
        )
        self.max_length = max_length

    def validate(self, value):
        value = super().validate(value)

        if value is None:
            return value

        if not isinstance(value, str):
            raise FieldValidationError("This field expects a string")
        
        if self.max_length and len(value) > self.max_length:
            raise FieldValidationError(f"Must be at most {self.max_length} characters")

        return value


class EmailField(CharField):
    def validate(self, value):
        value = super().validate(value)
        value = value.strip()

        if not (isinstance(value, str) or re.match(r"^\S+@\S+\.\S+$", value)):
            raise FieldValidationError("This field expects a valid email")

        return value


class DateTimeField(Field):
    pass


class IntegerField(Field):
    def validate(self, value):
        value = super().validate(value)

        if value is None:
            return value

        if not isinstance(value, int):
            raise FieldValidationError("This field expects an integer")

        return value


class Serializer:
    fields = {}

    def __init__(self, data):
        self.initial_data = data or {}
        self.validated_data = {}
        self.error_dict = {}

    def is_valid(self):
        self.validated_data = {}
        self.error_dict = {}

        for name, field in self.fields.items():
            if name not in self.initial_data:
                continue

            value = self.initial_data.get(name)

            if field.required and value in (None, ""):
                self.error_dict[name] = "This field is required"
                continue

            try:
                self.validated_data[name] = field.validate(value)
            except FieldValidationError as error:
                self.error_dict[name] = str(error)

        return not self.error_dict
    
    @property
    def error_message(self):
        return ', '.join(
            f'{k.capitalize()} {v.lower()}'
            for k, v in self.error_dict.items()
        )
