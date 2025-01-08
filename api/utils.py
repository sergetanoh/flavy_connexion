from django.conf import settings
from datetime import datetime, timedelta
# from django.contrib.gis.db.models.functions import Distance
# from django.contrib.gis.geos import Point
from .models import Pharmacie
from django.db.models import F
import re
import json
import random
import os
import string
import requests
from django.core import serializers
from .serializers import NotificationSerializer
from .models import Invoice, InvoicePayment
import firebase_admin
from firebase_admin import credentials, messaging
from twilio.rest import Client
from django.http import JsonResponse
import boto3
from django.conf import settings
from botocore.exceptions import ClientError

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


def has_key_client(errors):
    if isinstance(errors, dict):
        if "user" in errors:
            if "email" in errors["user"]:
               return  {'detail': "email: "+ errors["user"]["email"][0] }
           
            if "username" in errors["user"]:
               return  {'detail': "username: "+ errors["user"]["username"][0] }
           
            if "password" in errors["user"]:
               return  {'detail': "password: "+ errors["user"]["password"][0] }
           
            if "is_pharmacy" in errors["user"]:
               return  {'detail': "is_pharmacy: "+ errors["user"]["is_pharmacy"][0] }
           
        if "prenom" in errors:
            return  {'detail': "prenom: "+ errors["prenom"][0] }
        
        if "adresse" in errors:
            return  {'detail':"adresse: "+  errors["adresse"][0] }
        
        if "ville" in errors:
            return  {'detail':"ville: "+  errors["ville"][0] }
        
        if "phone" in errors:
            return  {'detail':"phone: "+  errors["phone"][0] }
        
        
        if "image" in errors:
            return  {'detail': "image: "+ errors["image"][0] }
        
        if "n_cmu" in errors:
            return  {'detail':"n_cmu: "+  errors["n_cmu"][0] }
        
        if "n_assurance" in errors:
            return  {'detail': "n_assurance: "+ errors["n_assurance"][0] }
        
        if "sexe" in errors:
            return  {'detail': "sexe: "+ errors["sexe"][0] }
        
        if "maladie_chronique" in errors:
            return  {'detail':  "maladie_chronique: "+ errors["maladie_chronique"][0] }
        
        if "poids" in errors:
            return  {'detail':"poids: "+  errors["poids"][0] }

def has_key_pharmacie(errors):
    if isinstance(errors, dict):
        if "user" in errors:
            if "email" in errors["user"]:
               return  {'detail': "email: "+ errors["user"]["email"][0] }
           
            if "username" in errors["user"]:
               return  {'detail': "username: "+ errors["user"]["username"][0] }
           
            if "password" in errors["user"]:
               return  {'detail': "password: "+ errors["user"]["password"][0] }
           
            if "is_pharmacy" in errors["user"]:
               return  {'detail': "is_pharmacy: "+ errors["user"]["is_pharmacy"][0] }
           
        if "num_pharmacie" in errors:
            return  {'detail': "num_pharmacie: "+ errors["num_pharmacie"][0] }
        
        if "nom_pharmacie" in errors:
            return  {'detail':"nom_pharmacie: "+  errors["nom_pharmacie"][0] }
        
        if "adresse_pharmacie" in errors:
            return  {'detail':"adresse_pharmacie: "+  errors["adresse_pharmacie"][0] }
        
        if "commune_pharmacie" in errors:
            return  {'detail':"commune_pharmacie: "+  errors["commune_pharmacie"][0] }
        
        
        if "image" in errors:
            return  {'detail': "image: "+ errors["image"][0] }
        
        if "n_cmu" in errors:
            return  {'detail':"n_cmu: "+  errors["n_cmu"][0] }
        
        if "n_assurance" in errors:
            return  {'detail': "n_assurance: "+ errors["n_assurance"][0] }
        
        if "ville_pharmacie" in errors:
            return  {'detail': "ville_pharmacie: "+ errors["ville_pharmacie"][0] }
        
        if "numero_contact_pharmacie" in errors:
            return  {'detail':  "numero_contact_pharmacie: "+ errors["numero_contact_pharmacie"][0] }
        
        if "horaire_ouverture_pharmacie" in errors:
            return  {'detail':"horaire_ouverture_pharmacie: "+  errors["horaire_ouverture_pharmacie"][0] }
 

def slugify(chaine):
    # Convertir en minuscules
    chaine = chaine.lower()
    # Remplacer les caractères spéciaux par des tirets
    chaine = re.sub(r'\s+', '-', chaine)  # Remplacer les espaces par des tirets
    chaine = re.sub(r'[^\w-]', '', chaine)  # Supprimer les caractères spéciaux sauf les tirets et les lettres/chiffres
    return chaine


def generer_code(name, nombre, longueur=6):
    code = str(nombre)
    if len(code) < longueur:
        code = '0' * (longueur - len(code)) + code
    name = slugify(name)
    newCode = name.upper()+"-"+code
    return newCode

def resend_notification(notification, token_phone):
    
    url = "https://fcm.googleapis.com/fcm/send"
    token = token_phone
    server_key = "AAAATipVc90:APA91bEYeNeVqZTimh-EgSc16QsqwjiQ3c4rXXSqeeq8hCrwK9V2vCnNIYMB9zrUpQC1YUmO1R0kvNURgTPyXnDILHUkjS11g4gW3PJuSYKEdRvKb1yKVdWtXyNMnBhemYBQk0flGeiq"

    title = notification.title
    body = notification.message

    notification_data = {'title': title, 'body': body, 'sound': 'default', 'badge': '1'}
    data_to_send = {
        'to': token,
        'notification': notification_data,
        'priority': 'high',
        'data': {
            'click_action': 'FLUTTER_NOTIFICATION_CLICK',
            'sound': 'default',
            'status': 'done',
            'screen': 'NotificationsScreen',
            'notification_type' : notification.type,
            'notification_id' : notification.id,
            'meta_data_id' : notification.data_id,
            'notification' : NotificationSerializer(notification, many=False).data,
            "title" : title,
            "body" : body,

        },
        "android": {
            "notification": {
                "channel_id": 'channel_id'  
            }
        }
    }

    print(data_to_send)

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'key=' + server_key
    }

    try:
        response = requests.post(url, data=json.dumps(data_to_send), headers=headers, timeout=1)
        print('FCM Response:', response)
        response.raise_for_status()
       
    except requests.exceptions.RequestException as e:
        print('FCM Send Error:', e)

def initialize_firebase():
    """
    Initialise Firebase Admin SDK avec la clé de compte de service.
    
    :param service_account_path: Chemin vers le fichier JSON de la clé de compte de service.
    """
    # Obtenir le chemin absolu vers le fichier JSON
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Chemin racine du projet
    service_account_path = os.path.join(BASE_DIR, "assets", "flavy-83d2e-533998492aef.json")

    cred = credentials.Certificate(service_account_path)
    firebase_admin.initialize_app(cred)
    
def send_notification(notification, token_phone):
    """
    Envoie une notification push via Firebase Cloud Messaging (API v1).

    :param registration_token: Token d'enregistrement de l'appareil cible ou nom du topic.
    :param title: Titre de la notification.
    :param body: Corps (message) de la notification.
    :return: Résultat de l'envoi.
    """
    if not firebase_admin._apps:
        initialize_firebase()

    registration_token = token_phone
    title = notification.title 
    body = notification.message

    # Création du message
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        token=registration_token,  # Peut être un topic en remplaçant "token" par "topic".
    )

    # Envoi de la notification
    try:
        response = messaging.send(message)
        return response
    except Exception as e:
        print(f"Une erreur est survenue lors de l'envoi : {e}")
        return None


def generate_reference(length, type="invoice"):
    """
    Génère un code alphanumérique de la longueur spécifiée.

    :param length: Longueur de la chaîne à générer.
    :return: Chaîne alphanumérique générée.
    """
    characters = string.ascii_letters + string.digits  # Lettres (majuscules et minuscules) + chiffres
    ref = ''.join(random.choice(characters) for _ in range(length))

    if type == "invoice":
        item = Invoice.objects.filter(reference=ref).first()

    if type == "payment":
        item = InvoicePayment.objects.filter(reference=ref).first()

    if item:
        generate_reference(length)

    return ref


def send_sms(to_phone, message):
    """
    Envoie un SMS en utilisant Twilio.
    :param to_phone: Numéro de téléphone du destinataire (format E.164, ex: +1234567890)
    :param message: Texte du message à envoyer
    :return: Résultat de l'envoi ou une exception en cas d'échec
    """
    try:
        # Initialiser le client Twilio avec les clés du fichier settings
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

        # Envoyer le SMS
        message = client.messages.create(
            body=message,  # Contenu du message
            from_=settings.TWILIO_PHONE_NUMBER,  # Numéro Twilio
            to=to_phone  # Numéro de destination
        )

        return f"Message envoyé avec succès : {message.sid}"
    except Exception as e:
        return f"Une erreur s'est produite : {str(e)}"


def send_sms_jetfy(recipient,  message):
    try:
    
        # Vérifier si le numéro du destinataire commence par "+"
        if recipient.startswith('+'):
            recipient = recipient[1:]

        # Récupérer les configurations
        url =  "https://api.jetfy.net/api/v1/sms/send"
        token = settings.JETFY_API_TOKEN
        sender_id = settings.JETFY_SENDER_ID
        
        # Préparer les headers avec le token Bearer
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        # Préparer le payload pour l'API Jetfy
        payload = {
            'sender_id': sender_id,
            'recipient': recipient,
            'message': message
        }
        
        # Faire l'appel à l'API Jetfy
        response = requests.post(
            url,
            json=payload,
            headers=headers
        )
        
        # Vérifier la réponse de l'API
        if response.status_code == 200 or response.status_code == 201:
            return response.json()
        else:
            return response.json()
            
    except json.JSONDecodeError:
        return {
            'success': False,
            'error': 'Format JSON invalide'
        }
    except requests.RequestException as e:
        return {
            'success': False,
            'error': f'Erreur de connexion à l\'API Jetfy: {str(e)}'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def generate_payment_token():
   
    # URL de l'API externe pour générer le token
    url = "https://api.digitalpaye.com/v1/auth"  # Remplacez par l'URL réelle de l'API

    # Les en-têtes requis
    headers = {
        "X-Environment": "Production",
        'Content-Type': 'application/json',
        "Authorization": "Basic bGl2ZV9kaWdpdGFscGF5ZTk2NjM4MDo0NDliNjhiZi0xZWU5LTQwN2ItYTRiYS01YjU3ZDdiZGRhOTY=",
    }

    try:
        # Effectuer une requête POST à l'API
        response = requests.post(url, headers=headers)

        # Vérifiez si la requête a réussi
        if response.status_code == 200:
            bodydata = response.json()  # Décoder la réponse JSON
            return bodydata.data.token
        else:
            # Gérer les erreurs HTTP
            print(f"Une erreur s'est produite lors de la requête : {response.status_code}")
            return ""
    except Exception as e:
        # Gérer les erreurs inattendues
        print(f"Une erreur interne s'est produite : {str(e)}")
        return ""
    

def send_mobile_money_request(request):
    """
    Fonction Django pour envoyer une requête POST à l'API DigitalPaye
    pour une collecte Mobile Money.
    """

    # URL de l'API
    url = "https://api.digitalpaye.com/v1/collecte/mobile-money"

    # Token de l'utilisateur
    token = generate_payment_token()

    # Corps de la requête (données à envoyer)
    payload = {
        "transactionId": "DIGITAL-79110123018182",
        "customer": {
            "lastName": "GUEI",
            "firstName": "HELIE",
            "phone": "0777101308",
            "email": "elieguei225@gmail.com",
            "address": {
                "countryCode": "CI",
                "city": "Abidjan",
                "streetAddress": "Plateau Cocody"
            }
        },
        "payer": "0504675930",
        "amount": "600",
        "currency": "XOF",
        "operator": "MTN_MONEY_CI" #"WAVE_MONEY_CI"
    }

    # En-têtes de la requête
    headers = {
        "X-Environment": "Production",
        "Content-Type": "application/json",
        "Authorization": f"Bearer { token }"
    }

    try:
        # Effectuer une requête POST
        response = requests.post(url, json=payload, headers=headers)

        # Vérifiez si la requête a réussi
        if response.status_code == 200:
            return JsonResponse({
                "statusCode": response.status_code,
                "message": "Request successful",
                "data": response.json()
            })
        else:
            return JsonResponse({
                "statusCode": response.status_code,
                "message": "Request failed",
                "error": response.text
            }, status=response.status_code)

    except Exception as e:
        # Gérer les erreurs réseau ou internes
        return JsonResponse({
            "statusCode": 500,
            "message": "An error occurred",
            "error": str(e)
        }, status=500)


def calculer_frais(montant):
    """
    Calcule les frais selon les règles suivantes:
    - 2.5% du montant
    - Plus 1% du montant si ce 1% est supérieur à 200, sinon plus 200
    
    Args:
        montant (float): Le montant initial
        
    Returns:
        float: Le montant des frais calculés
    """
    # Calcul du 2.5%
    frais_fixes = int(montant) * montant * 0.025
    
    # Calcul du 1%
    un_pourcent = montant * 0.01
    
    # Ajout de 1% ou 200 selon la condition
    if un_pourcent > 200:
        frais_additionnels = un_pourcent
    else:
        frais_additionnels = 200
        
    # Total des frais
    frais_totaux = frais_fixes + frais_additionnels
    frais_arrondis = round(frais_totaux / 5) * 5
    
    return frais_arrondis

def upload_to_s3(file, filename):
    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME
    )
    
    try:
        file_path = f"images/{filename}"
        s3_client.upload_fileobj(
            file,
            settings.AWS_STORAGE_BUCKET_NAME,
            file_path,
            ExtraArgs={
                # 'ACL': 'public-read',
                'ContentType': file.content_type
            }
        )
        
        url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/{file_path}"
        return url
    except ClientError as e:
        raise Exception(f"Erreur lors de l'upload S3: {str(e)}")