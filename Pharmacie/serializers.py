from rest_framework import serializers
from django.contrib.auth import get_user_model


class PharmacieRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=100, min_length=8, style={'input_type': 'password'})
    
    class Meta:
        model = get_user_model()
        fields = ['email', 'username', 'password', 'num_pharmacie', 'nom_pharmacie', 'adresse_pharmacie', 'commune_pharmacie', 'ville_pharmacie', 'numero_contact_pharmacie', 'horaire_ouverture_pharmacie']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user_password = validated_data.get('password', None)
        db_instance = self.Meta.model(**validated_data)
        db_instance.set_password(user_password)
        db_instance.is_pharmacie = True
        db_instance.save()
        return db_instance

class UserLoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=100)
    username = serializers.CharField(max_length=100, read_only=True)
    password = serializers.CharField(max_length=100, min_length=8, style={'input_type': 'password'})
    token = serializers.CharField(max_length=255, read_only=True)
