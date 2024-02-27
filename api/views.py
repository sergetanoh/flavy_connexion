
from .serializers import ClientRegistrationSerializer,UserLoginSerializer,PharmacieRegistrationSerializer,CategorieProduitSerializer, ProduitSerializer,CommandePharmacieSerializer,CommandeClientSerializer,FactureSerializer,UserSerializer,get_pharmacieSerializer,CommandetousclientSerializer,CommandetouspharmacieSerializer,ConseilSerializer
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


# Importez le modèle Facture et le sérialiseur FactureSerializer
from .models import Facture
from .models import Client,User,Pharmacie,Categorie_Produit,Produit,Commande,Commandetous,Conseil

import jwt

from .permissions import IsPharmacieOrReadOnly,IsSuperUserOrReadOnly,IsClientOrReadOnly,IsPharmacieCanModifyCommande
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

class ClientRegistrationAPIView(APIView):
    serializer_class = ClientRegistrationSerializer

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
        request_body=ClientRegistrationSerializer,
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
                taille=serializer.validated_data['taille']
            )

            # Utilisez les tokens pour générer les cookies
            refresh = RefreshToken.for_user(new_user)
            data = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'detail': f"Client {new_client.prenom} enregistré avec succès!",
                'user_data':ClientRegistrationSerializer(new_client,many=False).data
            }
            response = Response(data, status=status.HTTP_201_CREATED)

            return response
        
        list_erreur=has_key_client(serializer.errors)
            
        
        return Response(list_erreur, status=status.HTTP_400_BAD_REQUEST)
 
 
 
 
 
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
                num_pharmacie=serializer.validated_data['num_pharmacie'],
                nom_pharmacie=serializer.validated_data['nom_pharmacie'],
                adresse_pharmacie=serializer.validated_data['adresse_pharmacie'],
                commune_pharmacie=serializer.validated_data['commune_pharmacie'],
                ville_pharmacie=serializer.validated_data['ville_pharmacie'],
                numero_contact_pharmacie=serializer.validated_data['numero_contact_pharmacie'],
                horaire_ouverture_pharmacie=serializer.validated_data['horaire_ouverture_pharmacie'],
            )
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

                response_data = {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'detail': 'Utilisateur connecté avec succès',
                }

                return Response(response_data, status=status.HTTP_200_OK)
            else:
                raise AuthenticationFailed('Le compte utilisateur n\'est pas actif.')
        else:
            raise AuthenticationFailed('Email ou mot de passe incorrect.')
        
        

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







########## creation de category de produit et de produit


class CategorieProduitAPIView(APIView):
    permission_classes = [IsSuperUserOrReadOnly]

    @swagger_auto_schema(
        operation_summary='Liste des catégories de produits',
        operation_description='Récupère la liste de toutes les catégories de produits.',
        responses={200: openapi.Response('Liste des catégories de produits', CategorieProduitSerializer(many=True))}
    )
    def get(self, request):
        categories = Categorie_Produit.objects.all()
        serializer = CategorieProduitSerializer(categories, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary='Créer une nouvelle catégorie de produit',
        operation_description='Crée une nouvelle catégorie de produit avec les données fournies.',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'Category': openapi.Schema(type=openapi.TYPE_STRING, description='Nom de la catégorie'),
                'Description': openapi.Schema(type=openapi.TYPE_STRING, description='Description de la catégorie'),
            },
            required=['Category', 'Description']
        ),
        responses={
            201: openapi.Response('Catégorie créée avec succès', CategorieProduitSerializer),
            400: openapi.Response('Erreur de validation', openapi.Schema(type=openapi.TYPE_OBJECT, properties={'error': openapi.Schema(type=openapi.TYPE_STRING)})),
        }
    )
    def post(self, request):
        serializer = CategorieProduitSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary='Mettre à jour une catégorie de produit existante',
        operation_description='Mise à jour d\'une catégorie de produit existante avec les données fournies.',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'Category': openapi.Schema(type=openapi.TYPE_STRING, description='Nom de la catégorie'),
                'Description': openapi.Schema(type=openapi.TYPE_STRING, description='Description de la catégorie'),
            },
            required=['Category', 'Description']
        ),
        responses={
            200: openapi.Response('Catégorie mise à jour avec succès', CategorieProduitSerializer),
            400: openapi.Response('Erreur de validation', openapi.Schema(type=openapi.TYPE_OBJECT, properties={'error': openapi.Schema(type=openapi.TYPE_STRING)})),
        }
    )
    def put(self, request, pk):
        category = Categorie_Produit.objects.get(pk=pk)
        serializer = CategorieProduitSerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary='Supprimer une catégorie de produit existante',
        operation_description='Supprime une catégorie de produit existante.',
        responses={
            204: openapi.Response('Catégorie supprimée avec succès'),
            404: openapi.Response('Catégorie non trouvée', openapi.Schema(type=openapi.TYPE_OBJECT, properties={'detail': openapi.Schema(type=openapi.TYPE_STRING)})),
        }
    )
    def delete(self, request, pk):
        category = Categorie_Produit.objects.get(pk=pk)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
    
    
class ProduitAPIView(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = [IsPharmacieOrReadOnly]

    @swagger_auto_schema(
        operation_summary='Liste des produits',
        operation_description='Récupère la liste de tous les produits.',
        responses={200: openapi.Response('Liste des produits', ProduitSerializer(many=True))}
    )
    def get(self, request):
        produits = Produit.objects.all()
        serializer = ProduitSerializer(produits, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary='Créer un nouveau produit',
        operation_description='Crée un nouveau produit avec les données fournies.',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'Id_Category': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID de la catégorie du produit'),
                'Nom': openapi.Schema(type=openapi.TYPE_STRING, description='Nom du produit'),
                'Description': openapi.Schema(type=openapi.TYPE_STRING, description='Description détaillée du produit'),
                'Prix_Unitaire': openapi.Schema(type=openapi.TYPE_NUMBER, description='Prix unitaire du produit'),
                'Quantite': openapi.Schema(type=openapi.TYPE_INTEGER, description='Quantité de produit disponible'),
                'Disponibilite': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Disponibilité du produit'),
                'Client_Cible': openapi.Schema(type=openapi.TYPE_STRING, description='Public cible du produit'),
                'Date_Exp': openapi.Schema(type=openapi.TYPE_STRING, description='Date d\'expiration du produit (Format : YYYY-MM-DD)'),
                'Date_Creation': openapi.Schema(type=openapi.TYPE_STRING, description='Date de création du produit (Format : YYYY-MM-DDTHH:MM:SS)'),
            },
            required=['Id_Category', 'Nom', 'Prix_Unitaire', 'Quantite', 'Disponibilite', 'Date_Exp', 'Date_Creation']
        ),
        responses={
            201: openapi.Response('Produit créé avec succès', ProduitSerializer),
            400: openapi.Response('Erreur de validation', openapi.Schema(type=openapi.TYPE_OBJECT, properties={'error': openapi.Schema(type=openapi.TYPE_STRING)})),
        }
    )
    def post(self, request):
        serializer = ProduitSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary='Mettre à jour un produit existant',
        operation_description='Mise à jour d\'un produit existant avec les données fournies.',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'Id_Category': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID de la catégorie du produit'),
                'Nom': openapi.Schema(type=openapi.TYPE_STRING, description='Nom du produit'),
                'Description': openapi.Schema(type=openapi.TYPE_STRING, description='Description détaillée du produit'),
                'Prix_Unitaire': openapi.Schema(type=openapi.TYPE_NUMBER, description='Prix unitaire du produit'),
                'Quantite': openapi.Schema(type=openapi.TYPE_INTEGER, description='Quantité de produit disponible'),
                'Disponibilite': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Disponibilité du produit'),
                'Client_Cible': openapi.Schema(type=openapi.TYPE_STRING, description='Public cible du produit'),
                'Date_Exp': openapi.Schema(type=openapi.TYPE_STRING, description='Date d\'expiration du produit (Format : YYYY-MM-DD)'),
                'Date_Creation': openapi.Schema(type=openapi.TYPE_STRING, description='Date de création du produit (Format : YYYY-MM-DDTHH:MM:SS)'),
            },
            required=['Id_Category', 'Nom', 'Prix_Unitaire', 'Quantite', 'Disponibilite', 'Date_Exp', 'Date_Creation']
        ),
        responses={
            200: openapi.Response('Produit mis à jour avec succès', ProduitSerializer),
            400: openapi.Response('Erreur de validation', openapi.Schema(type=openapi.TYPE_OBJECT, properties={'error': openapi.Schema(type=openapi.TYPE_STRING)})),
        }
    )
    def put(self, request, pk):
        produit = Produit.objects.get(pk=pk)
        serializer = ProduitSerializer(produit, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary='Supprimer un produit existant',
        operation_description='Supprime un produit existant.',
        responses={
            204: openapi.Response('Produit supprimé avec succès'),
            404: openapi.Response('Produit non trouvé', openapi.Schema(type=openapi.TYPE_OBJECT, properties={'detail': openapi.Schema(type=openapi.TYPE_STRING)})),
        }
    )
    def delete(self, request, pk):
        produit = Produit.objects.get(pk=pk)
        produit.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
    
    
###################### commande 



class CommandeAPIViewClient(APIView):
    permission_classes = [IsClientOrReadOnly]

    @swagger_auto_schema(
        operation_summary='Créer une nouvelle commande client',
        operation_description='Crée une nouvelle commande pour le client avec les données fournies.',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'produit': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID du produit'),
                'quantite': openapi.Schema(type=openapi.TYPE_INTEGER, description='Quantité de produits à commander'),
            },
            required=['produit', 'quantite']
        ),
        responses={
            201: openapi.Response('Commande créée avec succès', CommandeClientSerializer),
            400: openapi.Response('Erreur de validation', openapi.Schema(type=openapi.TYPE_OBJECT, properties={'detail': openapi.Schema(type=openapi.TYPE_STRING)})),
        }
    )
    def post(self, request):
        serializer = CommandeClientSerializer(data=request.data)
        if serializer.is_valid():
            # Vérifiez si le produit est toujours disponible avant de créer la commande
            produit = serializer.validated_data['produit']
            if produit.Quantite > 0:
                serializer.save(client=request.user.client_user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response({"detail": "Le produit n'est pas disponible en quantité suffisante."},
                                status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary='Lister les commandes du client',
        operation_description='Récupère la liste de toutes les commandes du client.',
        responses={200: openapi.Response('Liste des commandes du client', CommandeClientSerializer(many=True))}
    )
    def get(self, request):
        commandes = Commande.objects.filter(client=request.user.client_user)
        serializer = CommandeClientSerializer(commandes, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary='Modifier une commande client',
        operation_description='Modifie une commande client existante (si elle est encore en attente).',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'quantite': openapi.Schema(type=openapi.TYPE_INTEGER, description='Nouvelle quantité de produits à commander'),
                # Ajoutez d'autres champs à modifier si nécessaire
            },
            required=['quantite']
        ),
        responses={
            200: openapi.Response('Commande modifiée avec succès', CommandeClientSerializer),
            400: openapi.Response('Erreur de validation ou commande ne peut pas être modifiée', openapi.Schema(type=openapi.TYPE_OBJECT, properties={'detail': openapi.Schema(type=openapi.TYPE_STRING)})),
        }
    )
    def put(self, request, pk):
        commande = Commande.objects.get(pk=pk)

        # Vérifiez si la commande peut être modifiée
        if commande.statut == 'en_attente':
            serializer = CommandeClientSerializer(commande, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()

                # Ajoutez ici la logique pour générer le reçu lorsque la commande est marquée comme "livrée"
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"detail": "La commande ne peut pas être modifiée."}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary='Supprimer une commande client',
        operation_description='Supprime une commande client existante (si elle est encore en attente).',
        responses={
            204: openapi.Response('Commande supprimée avec succès'),
            400: openapi.Response('Commande ne peut pas être supprimée', openapi.Schema(type=openapi.TYPE_OBJECT, properties={'detail': openapi.Schema(type=openapi.TYPE_STRING)})),
        }
    )
    def delete(self, request, pk):
        commande = Commande.objects.get(pk=pk)

        # Vérifiez si la commande peut être supprimée
        if commande.statut == 'en_attente':
            commande.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"detail": "La commande ne peut pas être supprimée."}, status=status.HTTP_400_BAD_REQUEST)
        
        
        
        
        


class CommandeAPIViewPharmacie(APIView):
    permission_classes = [IsPharmacieCanModifyCommande]

    @swagger_auto_schema(
        operation_summary='Lister les commandes de la pharmacie',
        operation_description='Récupère la liste de toutes les commandes de la pharmacie.',
        responses={200: openapi.Response('Liste des commandes de la pharmacie', CommandePharmacieSerializer(many=True))}
    )
    def get(self, request):
        # Récupérez les commandes concernant la pharmacie actuelle
        commandes = Commande.objects.filter(produit__pharmacie=request.user.pharmacie_user)
        serializer = CommandePharmacieSerializer(commandes, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary='Modifier une commande de la pharmacie',
        operation_description='Modifie une commande de la pharmacie existante (si elle est encore modifiable).',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'statut': openapi.Schema(type=openapi.TYPE_STRING, description='Nouveau statut de la commande (en_attente ou en_cours)'),
                'date_livraison': openapi.Schema(type=openapi.TYPE_STRING, description='Nouvelle date de livraison (format : YYYY-MM-DD)'),
            },
            required=['statut']
        ),
        responses={
            200: openapi.Response('Commande de la pharmacie modifiée avec succès', CommandePharmacieSerializer),
            400: openapi.Response('Erreur de validation ou commande ne peut pas être modifiée', openapi.Schema(type=openapi.TYPE_OBJECT, properties={'detail': openapi.Schema(type=openapi.TYPE_STRING)})),
        }
    )
    def put(self, request, pk):
        commande = Commande.objects.get(pk=pk)

        # Créez un nouveau dictionnaire avec les champs que la pharmacie peut modifier
        allowed_statuts = ['en_attente', 'en_cours']
        if commande.statut in allowed_statuts:
            update_data = {
                'statut': request.data.get('statut'),
                'date_livraison': request.data.get('date_livraison')
            }

            # Vérifiez si le nouveau statut est autorisé
            serializer = CommandePharmacieSerializer(commande, data=update_data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"detail": f"La modification du statut vers {update_data['statut']} n'est pas autorisée."},
                            status=status.HTTP_400_BAD_REQUEST)

# Le reste du code du serializer reste inchangé
 


class CommandeDetailView(RetrieveAPIView):
    serializer_class = CommandeClientSerializer
    permission_classes = [IsClientOrReadOnly]

    def get_object(self):
        # Récupérer la commande associée à l'utilisateur connecté
        user = self.request.user
        return Commande.objects.filter(client=user).first()

    @swagger_auto_schema(
        operation_summary='Détails de la commande client',
        operation_description='Récupère les détails de la commande du client, génère le reçu si nécessaire.',
        responses={200: openapi.Response('Détails de la commande client', CommandeClientSerializer)}
    )
    def get(self, request, *args, **kwargs):
        # Récupérer la commande associée à l'utilisateur et la sérialiser
        instance = self.get_object()
        if instance:
            serializer = self.get_serializer(instance)

            # Vérifiez si le statut de la commande est "livrée" et si le reçu n'a pas été généré
            if instance.statut == 'livree' and not instance.generer_recu:
                # Générer le reçu
                recu = self.generer_recu(instance)

                # Mettez à jour l'attribut generer_recu
                instance.generer_recu = True
                instance.save()

                return HttpResponse(recu, content_type='text/html')

            return Response(serializer.data)
        else:
            return Response({"detail": "Aucune commande trouvée."}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_summary='Générer le reçu de la commande',
        operation_description='Génère le reçu de la commande client et crée une facture associée.',
        responses={
            200: openapi.Response('Reçu généré avec succès', openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_BINARY)),
            404: openapi.Response('Aucune commande trouvée', openapi.Schema(type=openapi.TYPE_OBJECT, properties={'detail': openapi.Schema(type=openapi.TYPE_STRING)})),
            400: openapi.Response('Erreur de validation ou commande ne peut pas être modifiée', openapi.Schema(type=openapi.TYPE_OBJECT, properties={'detail': openapi.Schema(type=openapi.TYPE_STRING)})),
        },
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={},
            required=[]
        ),
    )
    def generer_recu(self, commande):
        # Logique pour générer le reçu (peut-être un modèle Facture associé à la commande)
        montant_total = commande.produit.Prix_Unitaire * commande.quantite

        # Créez la facture
        facture_data = {
            'id_Commande': commande.id,
            'Date_Facture': datetime.now(),
            'Montant_Total_Facture': montant_total,
            'Informations_Client': commande.client,
            'Informations_pharmacie': commande.produit.pharmacie,
            'Nom_Produit': commande.produit.Nom,
            'Quantite_Produit': commande.quantite,
            'Prix_Unitaire_Produit': commande.produit.Prix_Unitaire,
            'Nom_Pharmacie': commande.produit.pharmacie.nom_pharmacie,  # Ajout de Nom_Pharmacie
            'Nom_Commande': commande.produit.Nom,  # Ajout de Nom_Commande
            'Statut_Paiement': 'Non payée',
        }


        facture_serializer = FactureSerializer(data=facture_data)
        if facture_serializer.is_valid():
            facture_serializer.save()

            # Peut-être renvoyer le reçu en réponse (à adapter selon vos besoins)
            template = loader.get_template('recu_template.html')
            context = {'facture': facture_serializer.data}
            recu = template.render(context)
            return recu  # Retourne le reçu au lieu de la réponse HTTP
        else:
            # Gérer les erreurs de sérialisation
            raise serializers.ValidationError(facture_serializer.errors)

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
        print(clt)
        serializer =CommandetousclientSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        
        commandes = Commandetous.objects.filter(client=request.user.client_user)
        serializer = CommandetousclientSerializer(commandes, many=True)
        return Response(serializer.data)
    
    
class GestionCommandeDetailClient(APIView):
    permission_classes = [IsClientOrReadOnly]
    def get_object(self, pk):
        try:
            return Commandetous.objects.get(pk=pk)
        except Commandetous.DoesNotExist:
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
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"detail": "La commande ne peut pas être supprimée car elle n'est plus en attente."}, status=status.HTTP_400_BAD_REQUEST)    
        
        
        

class CommandesPharmacietous(APIView):
    permission_classes = [IsPharmacieCanModifyCommande]
    
    def get(self, request):
        print("request.user") 
        print(request.user) 
       
        commandes = Commandetous.objects.filter(pharmacie_id=request.user.pharmacie_user.pk)
        
        serializer = CommandetouspharmacieSerializer(commandes, many=True)
        return Response(serializer.data)
        

class PharmacieDetail(APIView):
    permission_classes = [IsPharmacieCanModifyCommande]
    def get_object(self, pk):
        try:
            return Commandetous.objects.get(pk=pk)
        except Commandetous.DoesNotExist:
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
        return Response(status=status.HTTP_204_NO_CONTENT)        
    
    


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
        return Response(status=status.HTTP_204_NO_CONTENT)    
    
    
    

