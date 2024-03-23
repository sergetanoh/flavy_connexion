import re
import requests

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

def push_notification(token_phone, notification):
    # FCM API Url
    url = "https://fcm.googleapis.com/fcm/send"
    token = token_phone
    server_key = "AAAAV7gfwcQ:APA91bHQQkizuwwU969j7NMXlYjI6EPHFohIyEQC9fZ_FTGEeHgLyNYvIHsshdO-J75ppywW57VG0CRiIh4LUIlotlhEDW_XjeFf4xd0hyf44OzrVINS7xAN7mLjnsP1X8ibV1NAXE65"

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
            'screen': 'NotificationsScreen'
        },
        # Always include this part to play the custom sound
        "android": {
            "notification": {
                "channel_id": 'channel_id'  # NOTIFICATION CHANNEL ID WITH CUSTOM SOUND REFERENCE HERE
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
