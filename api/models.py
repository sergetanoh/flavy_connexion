from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from django.conf import settings

class UserManager(BaseUserManager):
    def create_user(self, email,password=None):
        if not email:
            raise ValueError('A user email is needed.')

        if not password:
            raise ValueError('A user password is needed.')

        email = self.normalize_email(email)
        user = self.model(email=email)
    
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None):
        if not email:
            raise ValueError('A user email is needed.')

        if not password:
            raise ValueError('A user password is needed.')

        user = self.create_user(email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user





class AccessToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

class RefreshToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)





class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=100, unique=True)
    username = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateField(auto_now_add=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    objects = UserManager()


    def __str__(self):
        return self.email


class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='client_user')
    SEXE_CHOICES = [
        ('Homme', 'Homme'),
        ('Femme', 'Femme'),
    ]
    
    Prenom = models.CharField(max_length=255)
    adresse = models.CharField(max_length=255)
    ville = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    image = models.CharField(max_length=255)
    id_type_assurance = models.IntegerField()
    n_cmu = models.CharField(max_length=255)
    n_assurance = models.CharField(max_length=255)
    sexe = models.CharField(max_length=10, choices=SEXE_CHOICES)
    maladie_chronique = models.TextField()
    poids = models.DecimalField(max_digits=5, decimal_places=2)
    taille = models.DecimalField(max_digits=5, decimal_places=2)
    
    



class Pharmacie(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='pharmacie_user')
    num_pharmacie = models.CharField(max_length=20, blank=True, null=True)
    nom_pharmacie = models.CharField(max_length=255, blank=True, null=True)
    adresse_pharmacie = models.CharField(max_length=255, blank=True, null=True)
    commune_pharmacie = models.CharField(max_length=100, blank=True, null=True)
    ville_pharmacie = models.CharField(max_length=100, blank=True, null=True)
    numero_contact_pharmacie = models.CharField(max_length=20, blank=True, null=True)
    horaire_ouverture_pharmacie = models.CharField(max_length=255, blank=True, null=True)
    

