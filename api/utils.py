from django.conf import settings
from datetime import datetime, timedelta
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from .models import Pharmacie
from django.db.models import F

import jwt

# def generate_access_token(user):
#     payload = {
#         'user_id': user.id,  # Utilisez l'ID de l'utilisateur associé au user
#         'exp': datetime.utcnow() + timedelta(days=1, minutes=0),
#         'iat': datetime.utcnow(),
#     }

#     access_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

#     return access_token

# def generate_refresh_token(user):
#     payload = {
#         'user_id': user.id,  # Utilisez l'ID de l'utilisateur associé au user
#         'exp': datetime.utcnow() + timedelta(days=7, minutes=0),
#         'iat': datetime.utcnow(),
#     }

#     refresh_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

#     return refresh_token


def pharmacies_within_radius(latitude, longitude, radius_in_km):
    
    # Convertir la latitude et la longitude en valeurs flottantes
    latitude = float(latitude)
    longitude = float(longitude)

    # Convertir la position géographique en un objet Point
    user_location = Point(longitude, latitude, srid=4326)  # WGS84 coordinate system

    # Calculer le rayon en mètres
    radius_in_meters = radius_in_km * 1000

    # Récupérer les clients dans le rayon donné
    pharmacies_within_radius = Pharmacie.objects.annotate(
        latitude_float=F('latitude'),  # Convertir le champ CharField en float
        longitude_float=F('longitude')  # Convertir le champ CharField en float
    ).annotate(
        distance=Distance('location', user_location)
    ).filter(distance__lte=radius_in_meters)

    return pharmacies_within_radius
