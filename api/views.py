
from .serializers import ClientSerializer, ClientUpdateSerializer ,UserLoginSerializer,PharmacieRegistrationSerializer, PharmacieUpdateSerializer, UserSerializer,get_pharmacieSerializer,CommandetousclientSerializer,CommandetouspharmacieSerializer,ConseilSerializer, RechercheSerializer,  NotificationSerializer
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
import datetime
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404
from django.conf import settings
from django.http import HttpResponse
from django.template import loader
from rest_framework import serializers
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
# import requests
# from .utils import pharmacies_within_radius
import re



# Importez le modèle Facture et le sérialiseur FactureSerializer

from .models import Client,User,Pharmacie,Commande,Conseil, Recherche, Notification

import jwt

from .permissions import IsPharmacieOrReadOnly,IsSuperUserOrReadOnly,IsClientOrReadOnly,IsPharmacieCanModifyCommande, IsPharmacieOrClient
from .backends import EmailBackend

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


class ClientRegistrationAPIView(APIView):
    serializer_class = ClientSerializer
    serializer_update = ClientUpdateSerializer

    example_request = {
        "user": {
            "email": "client@example.com",
            "username": "votre nom de famille",
            "password": "motdepasseclient",
            "is_pharmacy": False
        },
        "prenom": "John",
        "adresse": "123 Rue de la Ville",
        "ville": "Ville",
        "phone": "0123456789",
        "image": "lien_de_l_image.jpg",
        "n_cmu": "CMU123",
        "n_assurance": "Assurance123",
        "sexe": "Homme",
        "maladie_chronique": "Aucune",
        "poids": 75.5,
        "taille": 180.0
    }

    @swagger_auto_schema(
        request_body=ClientSerializer,
        manual_parameters=[
            openapi.Parameter(
                'example',
                openapi.IN_QUERY,
                description='Exemple de JSON pour l\'enregistrement',
                type=openapi.TYPE_STRING,
                example=example_request,
            ),
        ],
        responses={
            201: openapi.Response('Client enregistré avec succès', examples={
                'application/json': {
                    'detail': 'Client enregistré avec succès!',
                },
            }),
            400: openapi.Response('Erreur de validation', examples={
                'application/json': {
                    'error': 'Détails sur l\'erreur de validation',
                },
            }),
        },
        operation_summary='Enregistrement du client',
        operation_description='Cette vue vous permet d\'enregistrer un nouveau client.',
    )
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=False):
            # Créez et enregistrez un nouvel utilisateur
            numero=serializer.validated_data['num_pharmacie']
            print("numero")
            print(numero)
            if numero:
                pharmacie=Pharmacie.objects.filter(num_pharmacie=numero).first()
                print("pharmacie")
                print(pharmacie)
                
                
                if  not pharmacie:
                    return Response({"detail": "Désolé le numero de la pharmacie est incorrecte."}, status=status.HTTP_400_BAD_REQUEST)
                
            new_user = User.objects.create_user(
                    email=serializer.validated_data['user']['email'],
                    username=serializer.validated_data['user']['username'],
                    password=serializer.validated_data['user']['password'],
                    is_pharmacie=False
                )

                # Associez le nouvel utilisateur au modèle Client
                
            new_client = Client.objects.create(
                    user=new_user,
                    prenom=serializer.validated_data['prenom'],
                    adresse=serializer.validated_data['adresse'],
                    ville=serializer.validated_data['ville'],
                    phone=serializer.validated_data['phone'],
                    image=serializer.validated_data['image'],
                    n_cmu=serializer.validated_data['n_cmu'],
                    n_assurance=serializer.validated_data['n_assurance'],
                    sexe=serializer.validated_data['sexe'],
                    maladie_chronique=serializer.validated_data['maladie_chronique'],
                    poids=serializer.validated_data['poids'],
                    taille=serializer.validated_data['taille'],
                    num_pharmacie=serializer.validated_data['num_pharmacie']
                )

                # Utilisez les tokens pour générer les cookies
            refresh = RefreshToken.for_user(new_user)
            data = {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'detail': f"Client {new_client.prenom} enregistré avec succès!",
                    'user_data':ClientSerializer(new_client,many=False).data
                }
            response = Response(data, status=status.HTTP_201_CREATED)

            return response
            
        list_erreur=has_key_client(serializer.errors)
                
            
        return Response(list_erreur, status=status.HTTP_400_BAD_REQUEST)

class ClientUpdateAPIView(APIView):
    serializer_update = ClientUpdateSerializer
    
    def put(self, request):
        # Créez et enregistrez un nouvel utilisateur
        numero=serializer.validated_data['num_pharmacie']
        
        if 'num_pharmacie'  in request.data and request.data['num_pharmacie']:
            pharmacie=Pharmacie.objects.filter(num_pharmacie=request.data['num_pharmacie']).first()
        
            if  not pharmacie:
                return Response({"detail": "Désolé le numero de la pharmacie est incorrecte."}, status=status.HTTP_400_BAD_REQUEST)
            
        user = request.user
        if not user:
            return Response({'detail': "Désolé, vous n'êtes pas authentifié."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Modifier mot de passe User
        if 'user' in request.data and 'password' in request.data['user']:
            user.set_password(request.data['user']['password'])
            user.save()
            
        
        client = request.user.client_user
        
        for key in request.data:
            setattr(client, key, request.data[key])
            
        client.save()
            

        # Utilisez les tokens pour générer les cookies
        refresh = RefreshToken.for_user(user)
        data = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'detail': f"Client {new_client.prenom} modifié avec succès!",
                'user_data':ClientSerializer(client,many=False).data
            }
        return Response(data, status=status.HTTP_200_OK)

            

 
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
 

class PharmacieRegistrationAPIView(APIView):
    serializer_class = PharmacieRegistrationSerializer

    permission_classes = (AllowAny,)
    example_request = {
        "user": {
            "email": "pharmacie@example.com",
            "username": "nom du docteur de la pharmacie",
            "password": "motdepassepharmacie",
            "is_pharmacie": True
        },
        "num_pharmacie": "12345",
        "nom_pharmacie": "Pharmacie ABC",
        "adresse_pharmacie": "456 Rue de la Pharmacie",
        "commune_pharmacie": "Commune",
        "ville_pharmacie": "Ville",
        "numero_contact_pharmacie": "0123456789",
        "horaire_ouverture_pharmacie": "9h00 - 18h00"
    }

    @swagger_auto_schema(
        request_body=PharmacieRegistrationSerializer,
        manual_parameters=[
            openapi.Parameter(
                'example',
                openapi.IN_QUERY,
                description='Exemple de JSON pour l\'enregistrement de la pharmacie',
                type=openapi.TYPE_STRING,
                example=example_request,
            ),
        ],
        responses={
            201: openapi.Response('Pharmacie enregistrée avec succès', examples={
                'application/json': {
                    'detail': 'Pharmacie enregistrée avec succès!',
                },
            }),
            400: openapi.Response('Erreur de validation', examples={
                'application/json': {
                    'error': 'Détails sur l\'erreur de validation',
                },
            }),
        },
        operation_summary='Enregistrement de la pharmacie',
        operation_description='Cette vue vous permet d\'enregistrer une nouvelle pharmacie.',
    )
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=False):
            # Créez et enregistrez un nouvel utilisateur
            new_user = User.objects.create_user(
                email=serializer.validated_data['user']['email'],
                username=serializer.validated_data['user']['username'],
                password=serializer.validated_data['user']['password'],
                is_pharmacie=True
            )

            # Associez le nouvel utilisateur au modèle Pharmacie
            
            new_pharmacie = Pharmacie.objects.create(
                user=new_user,
                num_pharmacie="",
                nom_pharmacie=serializer.validated_data['nom_pharmacie'],
                adresse_pharmacie=serializer.validated_data['adresse_pharmacie'],
                commune_pharmacie=serializer.validated_data['commune_pharmacie'],
                ville_pharmacie=serializer.validated_data['ville_pharmacie'],
                numero_contact_pharmacie=serializer.validated_data['numero_contact_pharmacie'],
                horaire_ouverture_pharmacie=serializer.validated_data['horaire_ouverture_pharmacie'],
            )
            
            # Enregistrer code pharmacie
            code = generer_code(new_pharmacie.nom_pharmacie, new_pharmacie.pk, longueur=6)
            print(code)
            new_pharmacie.num_pharmacie = code
            new_pharmacie.save()
            
             
            refresh = RefreshToken.for_user(new_user)

            print(f"Pharmacie {new_pharmacie.nom_pharmacie} enregistrée avec succès!")
            
            data = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'detail': f"Pharmacie {new_pharmacie.nom_pharmacie} enregistrée avec succès!",
                'user_data':PharmacieRegistrationSerializer(new_pharmacie,many=False).data
                
            }
            response = Response(data, status=status.HTTP_201_CREATED)

            return response
        list_erreur=has_key_pharmacie(serializer.errors)
            
        
        return Response(list_erreur, status=status.HTTP_400_BAD_REQUEST)

class PharmacieUpdateAPIView(APIView):
    serializer_class = PharmacieUpdateSerializer

    permission_classes = [IsAuthenticated]
    def put(self, request):
        
        serializer = self.serializer_class(data=request.data)
        if request.user.is_pharmacie != True:
            return Response({ 'detail': "Vous ne pouvez pas effectuer cette action"}, status=status.HTTP_400_BAD_REQUEST)
        
        if serializer.is_valid(raise_exception=False):
            #   Modifier et enregistrez un nouvel utilisateur
            user = request.user
            if 'user' in request.data and 'password' in request.data['user']:
                user.set_password(request.data['user']['password'])
                user.save()
            
            # validateData = serializer.validated_data
            # Modifier les information du modèle Pharmacie
            # if 'user' in validateData:
            #      user_data = validateData.pop('user')
                
            pharmacie = request.user.pharmacie_user
            # print(pharmacie)
            # pharmacie.update(**validateData)
           
            pharmacie.nom_pharmacie=request.data['nom_pharmacie']
            pharmacie.adresse_pharmacie=request.data['adresse_pharmacie']
            pharmacie.commune_pharmacie=request.data['commune_pharmacie']
            pharmacie.ville_pharmacie=request.data['ville_pharmacie']
            pharmacie.numero_contact_pharmacie=request.data['numero_contact_pharmacie']
            pharmacie.horaire_ouverture_pharmacie=request.data['horaire_ouverture_pharmacie']
            pharmacie.degarde=request.data['degarde']
            pharmacie.save()
            
             
            refresh = RefreshToken.for_user(user)

            
            data = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'detail': f"Information Pharmacie {pharmacie.nom_pharmacie} modifiée avec succès!",
                'user_data':PharmacieRegistrationSerializer(pharmacie,many=False).data
                
            }
            response = Response(data, status=status.HTTP_201_CREATED)

            return response
        list_erreur=has_key_pharmacie(serializer.errors)
            
        
        return Response(list_erreur, status=status.HTTP_400_BAD_REQUEST)
        


class UserDetailView(RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary='Récupérer les informations de l\'utilisateur connecté',
        operation_description='Récupère les informations de l\'utilisateur connecté, y compris son ID, nom d\'utilisateur et email.',
        responses={
            200: openapi.Response('Informations utilisateur récupérées avec succès', UserSerializer),
            401: 'Non authentifié - L\'utilisateur doit être connecté pour accéder à cette ressource.',
        }
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class UserLoginAPIView(APIView):
    authentication_classes = []
    serializer_class = UserLoginSerializer
    permission_classes = (AllowAny,)

    example_request = {
        "email": "pharmacie@example.com",
        "password": "motdepasse",
    }

    @swagger_auto_schema(
        request_body=UserLoginSerializer,
        manual_parameters=[
            openapi.Parameter(
                'example',
                openapi.IN_QUERY,
                description='Exemple de JSON pour la connexion de l\'utilisateur',
                type=openapi.TYPE_STRING,
                example=example_request,
            ),
        ],
        responses={
            200: openapi.Response('Utilisateur connecté avec succès', examples={
                'application/json': {
                    'refresh': 'refresh_token',
                    'access': 'access_token',
                    'detail': 'Utilisateur connecté avec succès',
                },
            }),
            401: openapi.Response('Échec de l\'authentification', examples={
                'application/json': {
                    'error': 'Email ou mot de passe incorrect',
                },
            }),
        },
        operation_summary='Connexion de l\'utilisateur',
        operation_description='Cette vue vous permet de connecter un utilisateur existant.',
    )
    def post(self, request):
        email = request.data.get('email', None)
        user_password = request.data.get('password', None)

        if not user_password or not email:
            raise AuthenticationFailed('L\'email et le mot de passe de l\'utilisateur sont nécessaires.')

        user_instance = EmailBackend().authenticate(request, email=email, password=user_password)

        if user_instance is not None:
            if user_instance.is_active:
                refresh = RefreshToken.for_user(user_instance)
                
                if user_instance.is_pharmacie == True:
                    data = PharmacieRegistrationSerializer(user_instance.pharmacie_user,many=False).data
                else:
                    data = ClientSerializer(user_instance.client_user,many=False).data
                   
                response_data = {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'detail': 'Utilisateur connecté avec succès',
                    'user_data': data
                }

                return Response(response_data, status=status.HTTP_200_OK)
            else:
                raise AuthenticationFailed('Le compte utilisateur n\'est pas actif.')
        else:
            raise AuthenticationFailed('Email ou mot de passe incorrect.')

class UserByTokenViewAPI(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (AllowAny,)

    def post(self, request):

        if request.user.is_pharmacie == True:
            user = PharmacieRegistrationSerializer(request.user.pharmacie_user,many=False).data
        else:
            user = ClientSerializer(request.user.client_user, many=False).data
            
        # Si le token n'est pas fourni, renvoie une réponse indiquant que l'utilisateur est déjà déconnecté
        return Response({
            "detail": "utilisateur recuperée avec succès",
            'user_data': user
        }, status=status.HTTP_200_OK)   
        
class UserLogoutViewAPI(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        responses={
            200: openapi.Response('Déconnexion réussie', examples={
                'application/json': {
                    'message': 'Déconnexion réussie.',
                },
            }),
            400: openapi.Response('Erreur lors de la déconnexion', examples={
                'application/json': {
                    'error': 'Une erreur est survenue lors de la déconnexion.',
                },
            }),
            401: openapi.Response('Utilisateur déjà déconnecté', examples={
                'application/json': {
                    'message': 'L\'utilisateur est déjà déconnecté.',
                },
            }),
        },
        operation_summary='Déconnexion de l\'utilisateur',
        operation_description='Cette vue vous permet de déconnecter un utilisateur en invalidant son token d\'accès.',
    )
    def post(self, request):
        user_token = request.COOKIES.get('access_token', None)

        if user_token:
            try:
                # Ajoutez le token à la liste noire pour le rendre invalide
                RefreshToken(user_token).blacklist()

                # Supprimez le cookie d'accès
                response = Response()
                response.delete_cookie('access_token')
                response.data = {
                    'message': 'Déconnexion réussie.'
                }
                return response
            except Exception as e:
                # Gérer les erreurs si nécessaire
                return Response({'error': 'Une erreur est survenue lors de la déconnexion.'}, status=400)

        # Si le token n'est pas fourni, renvoie une réponse indiquant que l'utilisateur est déjà déconnecté
        response = Response()
        response.data = {
            'message': 'L\'utilisateur est déjà déconnecté.'
        }
        return response

class get_pharmacie(APIView):
  def get(self,request):
        pharmacie=Pharmacie.objects.all()
        serializer=get_pharmacieSerializer(pharmacie,many=True)
        return Response(serializer.data)
        
class GetPharmacieGarde(APIView):
    def get(self, request):
        # Récupérer les pharmacies de garde
        pharmacies_de_garde = Pharmacie.objects.filter(degarde=True)
            # Serializer les pharmacies de garde si elles existent
        serializer = get_pharmacieSerializer(pharmacies_de_garde, many=True)
        return Response(serializer.data)
      
class get_Conseil(APIView):
    def get(self,request):
        conseils = Conseil.objects.all()
        serializer = ConseilSerializer(conseils, many=True)
        return Response(serializer.data)


class PasserCommandeClient(APIView):
    permission_classes = [IsClientOrReadOnly]
    def post(self, request):
        clt=Client.objects.get(user=request.user.pk)
        request.data['client'] = clt.pk
        
        if clt.num_pharmacie:
            pharmacie = Pharmacie.objects.filter(num_pharmacie= clt.num_pharmacie).first()
            if pharmacie is None:
                return Response({"detail": "Désolé, votre pharmacie est introuvable."}, status=status.HTTP_400_BAD_REQUEST)
            request.data['pharmacie_id'] = pharmacie.pk
        else:
            return Response({"detail": "Désolé, veuillez d'abord renseigner le code de votre pharmacie."}, status=status.HTTP_400_BAD_REQUEST)
            

        serializer =CommandetousclientSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        
        commandes = Commande.objects.filter(client=request.user.client_user)
        serializer = CommandetousclientSerializer(commandes, many=True)
        return Response(serializer.data)
    
    
class GestionCommandeDetailClient(APIView):
    permission_classes = [IsClientOrReadOnly]
    def get_object(self, pk):
        try:
            return Commande.objects.get(pk=pk)
        except Commande.DoesNotExist:
            raise Http404
    
    def put(self, request, pk):
        commande = self.get_object(pk)
        
        # Vérifier si la commande peut être modifiée
        if commande.en_attente:
            clt=Client.objects.get(user=request.user.pk)
            request.data['client'] = clt.pk
            serializer = CommandetousclientSerializer(commande, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"detail": "La commande ne peut pas être modifiée car elle n'est plus en attente."}, status=status.HTTP_400_BAD_REQUEST)
        

    def delete(self, request, pk):
        commande = self.get_object(pk)
        
        # Vérifier si la commande peut être supprimée
        if commande.en_attente:
            commande.delete()
            return Response({"detail": "Commande supprimée avec succès"}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "La commande ne peut pas être supprimée car elle n'est plus en attente."}, status=status.HTTP_400_BAD_REQUEST)    

class CommandesPharmacietous(APIView):
    permission_classes = [IsPharmacieCanModifyCommande]
    
    def get(self, request):
        commandes = Commande.objects.filter(pharmacie_id=request.user.pharmacie_user.pk)
        
        
        serializer = CommandetouspharmacieSerializer(commandes, many=True)
        return Response(serializer.data)
        

class PharmacieDetail(APIView):
    permission_classes = [IsPharmacieCanModifyCommande]
    def get_object(self, pk):
        try:
            return Commande.objects.get(pk=pk)
        except Commande.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        customer = self.get_object(pk)
        serializer = CommandetouspharmacieSerializer(customer)
        return Response(serializer.data)

    def put(self, request, pk):
        commande = self.get_object(pk)
        request.data['pharmacie_id'] =  commande.pharmacie_id
        request.data['client'] =  commande.client
        
        serializer = CommandetouspharmacieSerializer(commande, data=request.data)
        if serializer.is_valid():
            if request.data.get('statut')=='livree' and not commande.en_attente:
                return Response({"detail": "La commande a déjà été validée."}, status=status.HTTP_400_BAD_REQUEST)
            
            if request.data.get('facture'):
                # Valider la commande
                commande.en_attente = False
                commande.statut = 'traite'
                commande.Facture = request.data.get('facture')
                commande.save()
                return Response(serializer.data)
            
            if request.data.get('statut'):
                commande.statut = request.data.get('statut')
                if request.data.get('statut') == "termine":
                    commande.termine = True
                commande.save()
                
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        customer = self.get_object(pk)
        customer.delete()
        return Response({"detail": "Utilisateur supprimée avec succès"}, status=status.HTTP_200_OK)        
    
class ConseilDetail(APIView):
    permission_classes = [IsPharmacieCanModifyCommande]
    
    def get_object(self, pk):
        try:
            return Conseil.objects.get(pk=pk)
        except Conseil.DoesNotExist:
            raise Http404

    
    def get(self, request, pk):
        conseil = self.get_object(pk)
        serializer = ConseilSerializer(conseil)
        return Response(serializer.data)
    
    def post(self, request):
        phar=Pharmacie.objects.get(user=request.user.pk)
        request.data['pharmacie'] = phar.pk
        serializer = ConseilSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    def put(self, request, pk):
        
        conseil = self.get_object(pk)
        phar=Pharmacie.objects.get(user=request.user.pk)
        request.data['pharmacie'] = phar.pk
        serializer = ConseilSerializer(conseil, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    def delete(self, request, pk):
        conseil = self.get_object(pk)
        conseil.delete()
        return Response({"detail": "Conseil supprimé avec succès"}, status=status.HTTP_200_OK)    
    
class RechercheList(APIView):
    permission_classes = [IsPharmacieOrClient]
    
    def get(self, request):
        if request.user.is_pharmacie == True:
            recherches = Recherche.objects.filter(Q(pharmacie_id=request.user.pharmacie_user.pk) | Q(en_attente=True)).order_by("-pk")
        else:
            recherches = Recherche.objects.filter(client=request.user.client_user.pk).order_by("-pk")
        
        
        serializer = RechercheSerializer(recherches, many=True)
        return Response(serializer.data)

    def post(self, request):
        request.data["client"]=request.user.client_user.pk
        serializer = RechercheSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RechercheDetail(APIView):
    permission_classes = [IsPharmacieOrClient]
    
    def get_object(self, pk):
        try:
            return Recherche.objects.get(pk=pk)
        except Recherche.DoesNotExist:
            # raise Http404
            return Response({"detail":"Recherche introuvable"}, status=status.HTTP_404_NOT_FOUND)

    def get(self, request, pk):
        recherche = self.get_object(pk)
        
        # Verifier si pharmacie
        if request.user.is_pharmacie == True :
            # Verifier si recherche traitée par d'autre pharmacie
            if recherche.en_attente == False and recherche.pharmacie_id != request.user.pharmacie_user.pk:
                return Response({"detail":"Désolé, vous ne pouvez accéder à cette recherche"}, status=status.HTTP_403_FORBIDDEN)
        else:
            if recherche.client.pk != request.user.client_user.pk:
                return Response({"detail":"Désolé, vous ne pouvez accéder à cette recherche"}, status=status.HTTP_403_FORBIDDEN)
        serializer = RechercheSerializer(recherche)
        return Response(serializer.data)

    def put(self, request, pk):
        recherche = self.get_object(pk)
        request.data['client'] = recherche.client.pk
        if recherche.terminer == True:
            return Response({"detail":"Cette recherche est déjà terminée"}, status=status.HTTP_400_BAD_REQUEST)
        if request.user.is_pharmacie == True :
            # return Response({"detail":"Désolé, vous ne pouvez effectuer à cette action"}, status=status.HTTP_403_FORBIDDEN)
            if  not('facture' in request.data) or not(request.data['facture']):
                return Response({"detail":"La facture est obligatoire"}, status=status.HTTP_400_BAD_REQUEST)
            request.data['statut'] = "traite"
            request.data['en_attente'] = False
            request.data['pharmacie_id'] = request.user.pharmacie_user.pk
            
        if request.user.is_pharmacie != True :
            if recherche.client.pk != request.user.client_user.pk:
                return Response({"detail":"Désolé, vous ne pouvez effectuer à cette action"}, status=status.HTTP_403_FORBIDDEN)
            print('terminer' in request.data)
            if  not('terminer' in request.data) or request.data['terminer'] == False:
                return Response({"detail":"Requete incorrecte"}, status=status.HTTP_400_BAD_REQUEST)
    
        
        serializer = RechercheSerializer(recherche, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        recherche = self.get_object(pk)
        if request.user.is_pharmacie != True :
            if recherche.client.pk != request.user.client_user.pk:
                return Response({"detail":"Désolé, vous ne pouvez effectuer à cette action"}, status=status.HTTP_403_FORBIDDEN)
        recherche.delete()
        return Response({"detail": "Recherche supprimée avec succès"},status=status.HTTP_200_OK)

class NotificationList(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (AllowAny,)
    
    def get(self, request):
        if request.user:
            if request.user.is_pharmacie != True:
                notifications = Notification.objects.filter(user_type='client').filter(user_id=request.user.client_user.pk).order_by("-pk")
            else:
                notifications = Notification.objects.filter(user_type='pharmacie').filter(user_id=request.user.pharmacie_user.pk).order_by("-pk")
            
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)

    def post(self, request):
        data=request.data
        if request.user.is_pharmacie != True:
            data['user_type'] = 'client'
            data['user_id'] = request.user.client_user.pk
        else:
            data['user_type'] = 'pharmacie'
            data['user_id'] = request.user.pharmacie_user.pk
            
            
        serializer = NotificationSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class NotificationDetail(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (AllowAny,)
    
    def get_object(self, pk):
        try:
            return Notification.objects.get(pk=pk)
        except Notification.DoesNotExist:
            raise Http404
        

    def get(self, request, pk):
        notification = self.get_object(pk)
        serializer = NotificationSerializer(notification)
        return Response(serializer.data)

    def put(self, request, pk):
        data=request.data
        
        # notification = Notification.objects.get(pk=pk).update(**data)
        notification = self.get_object(pk)
        
        # Mettre à jour les attributs de l'objet avec les valeurs fournies dans le dictionnaire
        for key in request.data:
            setattr(notification, key, request.data[key])
            
        # Enregistrer l'objet mis à jour dans la base de données
        notification.save()

        # notification.update(**data)
        return Response(NotificationSerializer(notification,many=False).data)

    def delete(self, request, pk):
        notification = self.get_object(pk)
        notification.delete()
        return Response({'detail': "Notification supprimée"},status=status.HTTP_200_OK)
