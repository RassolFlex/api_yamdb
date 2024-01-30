import re
import datetime

from rest_framework import serializers
from django.core.exceptions import ValidationError

from .constants import LENGTH_FOR_FIELD


def check_username(username):
    """Функция проверки username."""

    if not username:
        raise serializers.ValidationError('Username must be not empty.')
    if len(username) > LENGTH_FOR_FIELD:
        raise serializers.ValidationError('Username over 150 length.')
    if username == 'me':
        raise serializers.ValidationError(
            'Username should not be equal "me".')
    pattern = r'^[\w.@+-]+\Z'
    if not re.match(pattern, username):
        raise serializers.ValidationError('Invalid username.')
    return username


def year_validator(value):
    if value > datetime.datetime.now().year:
        raise ValidationError(
            f'Invalid year: {value}'
        )
