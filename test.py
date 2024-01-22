"""
import requests

# URL de l'API pour la connexion
login_url = "http://localhost:8000/api/user/login/"

# Données à envoyer dans la requête POST pour la connexion
login_data = {
    "email": "pharmacie01@gmail.com",
    "password": "serge"

}

# Effectuer la requête POST pour la connexion
login_response = requests.post(login_url, json=login_data)

# Afficher la réponse de la connexion
print(login_response.status_code)
print(login_response.json())
"""


import requests
from getpass import getpass
endpoint='http://localhost:8000/auth'

username=input("entrez votre username :")

password=getpass("entrez votre mot de passe :")
auth_esponse=requests.post(endpoint,json={'username':username,'password':password})

print(auth_esponse.json()) 
print(type(auth_esponse.status_code))
if auth_esponse.status_code ==200:
    response=requests.get(endpoint)
    print(response.json())
    print(response.status_code)