from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin


from django.conf import settings

class UserManager(BaseUserManager):
    def create_user(self, email,username,password=None,is_pharmacie=False,):
        if not email:
            raise ValueError('A user email is needed.')

        if not password:
            raise ValueError('A user password is needed.')

        email = self.normalize_email(email)
        user = self.model(email=email, username=username,is_pharmacie=is_pharmacie)
      
    
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email,username, password=None, **extra_fields):
        if not email:
            raise ValueError('A user email is needed.')

        user = self.create_user(email=email, username=username ,password=password, **extra_fields)
        user.is_superuser = True
        user.is_staff = True
        user.is_pharmacie = False
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=100, unique=True)
    username = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    date_joined = models.DateField(auto_now_add=True)
    date_update =  models.DateTimeField(auto_now=True)
    is_pharmacie = models.BooleanField(default=False)  # Nouveau champ
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    

    objects = UserManager()


    def __str__(self):
        return self.email


class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,  related_name='client_user')
    SEXE_CHOICES = [
        ('Homme', 'Homme'),
        ('Femme', 'Femme'),
    ]
    
    prenom = models.CharField(max_length=255)
    adresse = models.CharField(max_length=255)
    ville = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    image = models.CharField(max_length=255)
    n_cmu = models.CharField(max_length=255,null=True, blank=True)
    n_assurance = models.CharField(max_length=255,null=True, blank=True)
    sexe = models.CharField(max_length=10, choices=SEXE_CHOICES)
    maladie_chronique = models.TextField(null=True, blank=True)
    poids = models.DecimalField(max_digits=5, decimal_places=2,null=True, blank=True)
    taille = models.DecimalField(max_digits=5, decimal_places=2,null=True, blank=True)
    num_pharmacie=models.CharField(max_length=255, blank=True, null=True)
    firebase_token=models.CharField(max_length=255, blank=True, null=True)
    
    est_actif = models.BooleanField(default=True)
    date_creation =  models.DateTimeField(auto_now_add=True, blank=True, null=True)
    date_modification =  models.DateTimeField(auto_now=True, blank=True, null=True)
    
    
class Pharmacie(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,  related_name='pharmacie_user')
    num_pharmacie = models.CharField(max_length=20, blank=True, null=True)
    nom_pharmacie = models.CharField(max_length=255, blank=True, null=True)
    adresse_pharmacie = models.CharField(max_length=255, blank=True, null=True)
    commune_pharmacie = models.CharField(max_length=100, blank=True, null=True)
    ville_pharmacie = models.CharField(max_length=100, blank=True, null=True)
    numero_contact_pharmacie = models.CharField(max_length=20, blank=True, null=True)
    horaire_ouverture_pharmacie = models.CharField(max_length=255, blank=True, null=True)
    degarde=models.BooleanField(default=False)
    latitude=models.CharField(max_length=100, blank=True, null=True)
    longitude=models.CharField(max_length=100, blank=True, null=True)
    logo_url=models.CharField(max_length=100, default="https://media.istockphoto.com/id/1275720974/vector/blue-and-green-medical-cross-health.jpg?s=612x612&w=0&k=20&c=j322qhLcySdh7qhtlTnUf_EUzlQG2i9bnoJ3vHdJ81I=")
    firebase_token=models.CharField(max_length=255, blank=True, null=True)
    
    est_actif = models.BooleanField(default=True)
    date_creation =  models.DateTimeField(auto_now_add=True, blank=True, null=True)
    date_modification =  models.DateTimeField(auto_now=True, blank=True, null=True)
    
    def __str__(self):
        return f"{self.nom_pharmacie}"
    

class Commande(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('traite', 'Traité'),
        ('en_cours', 'En cours de livraison'),
        ('livree', 'Livrée'),
        ('termine', 'Terminé'),
        ('annulee', 'Annulée'),
    ]

    pharmacie_id = models.ForeignKey(Pharmacie, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    ordornance=models.CharField(max_length=255, blank=True, null=True)
    nom_medicament=models.CharField(max_length=255, blank=True, null=True)
    description=models.TextField(blank=True, null=True)
    quantite = models.PositiveIntegerField(default=1)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    en_attente=models.BooleanField(default=True)
    terminer=models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_livraison = models.DateTimeField(null=True, blank=True)
    Facture=models.CharField(max_length=255, blank=True, null=True)
    
    est_actif = models.BooleanField(default=True)
    date_modification =  models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return f"Commande {self.id} - {self.client.prenom}"    


class Conseil(models.Model):
    titre = models.CharField(max_length=100)
    message = models.TextField()
    pharmacie = models.ForeignKey(Pharmacie, on_delete=models.CASCADE)
    date_creation = models.DateTimeField(auto_now_add=True)
    est_actif = models.BooleanField(default=True)
    date_modification =  models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.titre
    
    
class Recherche(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('traite', 'Traité'),
        ('termine', 'Terminé'),
        ('annulee', 'Annulée'),
    ]
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    ordonnance = models.CharField(max_length=255, blank=True, null=True)
    nom_medicament = models.CharField(max_length=255, blank=True, null=True)
    quantite =  models.PositiveIntegerField(default=1)
    description = models.TextField(blank=True, null=True)
    statut = models.CharField(max_length=255, choices=STATUT_CHOICES, default='en_attente')
    en_attente = models.BooleanField(default=True)
    terminer = models.BooleanField(default=False)
    pharmacie_id = models.ForeignKey(Pharmacie, on_delete=models.SET_NULL, blank=True, null=True)
    facture =  models.TextField(blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True, blank=True, null=True )
    date_modification = models.DateTimeField(auto_now=True, blank=True, null=True)
    est_actif = models.BooleanField(default=True)
   
    def __str__(self):
        return "Recherche #"+str(self.pk)
    
    
class Notification(models.Model):
    STATUT_CHOICES = [
        ('client', 'Client'),
        ('pharmacie', 'Pharmacie')
    ]
    title = models.CharField(max_length=255)
    message = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    data_id = models.CharField(max_length=255, blank=True, null=True)
    metadata = models.CharField(max_length=255, blank=True, null=True)
    is_read = models.BooleanField(default=False)
    user_type = models.CharField(max_length=255, choices=STATUT_CHOICES)
    user_id = models.PositiveIntegerField()

    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    est_actif = models.BooleanField(default=True)
   
    def __str__(self):
        return str(self.title)