import re
import json
import random
import string
import requests
from django.core import serializers
from .serializers import NotificationSerializer
from .models import Invoice

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

def send_notification(notification, token_phone):
    
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

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'key=' + server_key
    }

    try:
        response = requests.post(url, data=json.dumps(data_to_send), headers=headers, timeout=1)
        response.raise_for_status()
       
    except requests.exceptions.RequestException as e:
        print('FCM Send Error:', e)


def generate_reference(length):
    """
    Génère un code alphanumérique de la longueur spécifiée.

    :param length: Longueur de la chaîne à générer.
    :return: Chaîne alphanumérique générée.
    """
    characters = string.ascii_letters + string.digits  # Lettres (majuscules et minuscules) + chiffres
    ref = ''.join(random.choice(characters) for _ in range(length))

    invoice = Invoice.objects.filter(reference=ref).first()
    if invoice:
        generate_reference(length)

    return ref


