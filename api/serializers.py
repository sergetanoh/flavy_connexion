from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Client,Pharmacie
from .models import Categorie_Produit, Produit,Commande,Facture,Commandetous,Conseil
import pdb

class UserSerializer(serializers.ModelSerializer):
	password = serializers.CharField(max_length=100, min_length=8, style={'input_type': 'password'})
	class Meta:
		model = get_user_model()
		fields = ['email', 'username', 'password']

	def create(self, validated_data):
		user_password = validated_data.get('password', None)
		db_instance = self.Meta.model(email=validated_data.get('email'), username=validated_data.get('username'))
		db_instance.set_password(user_password)
		db_instance.save()
		return db_instance

# Ajoutez un champ 'fullname' dans le serializer ClientSerializer
class ClientRegistrationSerializer(serializers.ModelSerializer):
    SEXE_CHOICES = [
        ('Homme', 'Homme'),
        ('Femme', 'Femme'),
    ]

    # On ajoute le champ 'user' avec le sérialiseur UserSerializer
    user = UserSerializer()

    class Meta:
        model = Client
        fields = ['user', 'prenom', 'adresse', 'ville', 'phone', 'image', 'n_cmu', 'n_assurance', 'sexe', 'maladie_chronique', 'poids', 'taille']
        extra_kwargs = {'date_inscription': {'read_only': True}}  # Empêche la modification de la date_inscription

    # On override la méthode create pour créer d'abord l'utilisateur puis le client
    def create(self, validated_data):
        # Extraire les données utilisateur du sérialiseur ClientSerializer
        user_data = validated_data.pop('user')

        # Créer un utilisateur avec les données extraites
        user = get_user_model().objects.create(**user_data)

        # Créer le client associé à cet utilisateur
        client = Client.objects.create(user=user, **validated_data)

        return client




class PharmacieRegistrationSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Pharmacie
        fields = ['user', 'num_pharmacie', 'nom_pharmacie', 'adresse_pharmacie', 'commune_pharmacie', 'ville_pharmacie', 'numero_contact_pharmacie', 'horaire_ouverture_pharmacie']

    def create(self, validated_data):
        # Extraire les données utilisateur du sérialiseur PharmacieSerializer
       


        user_data = validated_data.pop('user')
        
        # Créer un utilisateur avec les données extraites
        user = get_user_model().objects.create(**user_data)

        # Créer la pharmacie associée à cet utilisateur
        pharmacie = Pharmacie.objects.create(user=user, **validated_data)
        
        return pharmacie


class get_pharmacieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pharmacie
        fields = ['id', 'user', 'num_pharmacie', 'nom_pharmacie', 'adresse_pharmacie', 'commune_pharmacie', 'ville_pharmacie', 'numero_contact_pharmacie', 'horaire_ouverture_pharmacie', 'degarde']
       
  
  
  
  
class UserLoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=100)
    username = serializers.CharField(max_length=100, read_only=True)
    password = serializers.CharField(max_length=100, min_length=8, style={'input_type': 'password'})
    token = serializers.CharField(max_length=255, read_only=True)





class CommandetousclientSerializer(serializers.ModelSerializer):
    class Meta:
        model=Commandetous
        fields='__all__'
    
class CommandetouspharmacieSerializer(serializers.ModelSerializer):
    class Meta:
        model=Commandetous
        fields='__all__'
        
        
        


class CategorieProduitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categorie_Produit
        fields = ['id', 'Category', 'Description']

class ProduitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produit
        fields = ['id', 'Id_Category','Id_Pharmacie', 'Nom', 'Description', 'Prix_Unitaire', 'Quantite', 'Disponibilite', 'Client_Cible', 'Date_Exp', 'Date_Creation']


class CommandeClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Commande
        fields = ['id', 'produit','client', 'quantite', 'statut', 'date_livraison']
        read_only_fields = ['id',  'date_livraison', 'date_creation', 'client','statut','generer_recu']

        def update(self, instance, validated_data):
        # Autoriser la modification uniquement des champs spécifiques
            allowed_fields = ['produit','quantite']
            for field in allowed_fields:
                if field in validated_data:
                    setattr(instance, field, validated_data[field])

            instance.save()
            return instance
        
        
class CommandePharmacieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Commande
        fields = ['id', 'produit','client', 'quantite', 'statut', 'date_livraison']
        read_only_fields = ['id', 'produit', 'quantite', 'date_creation', 'client']

        def update(self, instance, validated_data):
        # Autoriser la modification uniquement des champs spécifiques
            allowed_fields = ['statut', 'date_livraison']
            for field in allowed_fields:
                if field in validated_data:
                    setattr(instance, field, validated_data[field])

            instance.save()
            return instance        
        
        
        

class FactureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Facture
        fields = '__all__'        
        
        
class ConseilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conseil
        fields = '__all__'