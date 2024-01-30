from django.conf import settings
from datetime import datetime, timedelta
import jwt

def generate_access_token(user):
    payload = {
        'user_id': user.id,  # Utilisez l'ID de l'utilisateur associé au user
        'exp': datetime.utcnow() + timedelta(days=1, minutes=0),
        'iat': datetime.utcnow(),
    }

    access_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

    return access_token

def generate_refresh_token(user):
    payload = {
        'user_id': user.id,  # Utilisez l'ID de l'utilisateur associé au user
        'exp': datetime.utcnow() + timedelta(days=7, minutes=0),
        'iat': datetime.utcnow(),
    }

    refresh_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

    return refresh_token
