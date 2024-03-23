from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Client,Pharmacie
from .models import Commande,Commande,Conseil, Recherche, Notification
import pdb

class UserSerializer(serializers.ModelSerializer):
	# password = serializers.CharField(max_length=100, min_length=8, style={'input_type': 'password'})
	class Meta:
		model = get_user_model()
		fields = ['email', 'username']
		# fields = ['email', 'username', 'password']

	def create(self, validated_data):
		user_password = validated_data.get('password', None)
		db_instance = self.Meta.model(email=validated_data.get('email'), username=validated_data.get('username'))
		db_instance.set_password(user_password)
		db_instance.save()
		return db_instance

# Ajoutez un champ 'fullname' dans le serializer ClientSerializer
class ClientSerializer(serializers.ModelSerializer):
    SEXE_CHOICES = [
        ('Homme', 'Homme'),
        ('Femme', 'Femme'),
    ]

    # On ajoute le champ 'user' avec le sérialiseur UserSerializer
    user = UserSerializer()

    class Meta:
        model = Client
        fields = "__all__"
        # fields = ['user', 'prenom', 'adresse', 'ville', 'phone', 'image', 'n_cmu', 'n_assurance', 'sexe', 'maladie_chronique', 'poids', 'taille','num_pharmacie', 'est_actif', 'date_creation', 'date_modification']
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

class PharmacieSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Pharmacie
        fields='__all__'
        # fields = ['user', 'num_pharmacie', 'nom_pharmacie', 'adresse_pharmacie', 'commune_pharmacie', 'ville_pharmacie', 'numero_contact_pharmacie', 'horaire_ouverture_pharmacie','num_pharmacie', 'degarde','latitude','longitude','logo_url','est_actif','date_creation' 'date_modification']

    def create(self, validated_data):
        # Extraire les données utilisateur du sérialiseur PharmacieSerializer
       


        user_data = validated_data.pop('user')
        
        # Créer un utilisateur avec les données extraites
        user = get_user_model().objects.create(**user_data)

        # Créer la pharmacie associée à cet utilisateur
        pharmacie = Pharmacie.objects.create(user=user, **validated_data)
        
        return pharmacie
    
class UserLoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=100)
    username = serializers.CharField(max_length=100, read_only=True)
    password = serializers.CharField(max_length=100, min_length=8, style={'input_type': 'password'})
    token = serializers.CharField(max_length=255, read_only=True)



class CommandeSerializer(serializers.ModelSerializer):
    client = ClientSerializer()
    class Meta:
        model=Commande
        fields='__all__'
      
        
class ConseilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conseil
        fields = '__all__'
        

class RechercheSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recherche
        fields = '__all__'
        
        
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'