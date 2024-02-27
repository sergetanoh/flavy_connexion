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
    


    
    
    
    


class Categorie_Produit(models.Model):
    Category = models.CharField(max_length=255)
    Description = models.TextField()

    def __str__(self):
        return self.Category

class Produit(models.Model):
    Id_Category = models.ForeignKey(Categorie_Produit, on_delete=models.CASCADE)
    Id_Pharmacie = models.ForeignKey(Pharmacie, on_delete=models.CASCADE)  # Ajout de la référence à la pharmacie
    Nom = models.CharField(max_length=255)
    Description = models.TextField()
    Prix_Unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    Quantite = models.PositiveIntegerField()
    Disponibilite = models.BooleanField(default=True)
    Client_Cible = models.CharField(max_length=255)
    Date_Exp = models.DateField()
    Date_Creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.Nom
    
    
    

class Commandetous(models.Model):
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
    quantite = models.PositiveIntegerField(default=1)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    en_attente=models.BooleanField(default=True)
    terminer=models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_livraison = models.DateTimeField(null=True, blank=True)
    Facture=models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Commande {self.id} - {self.client.prenom}"    





class Commande(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('en_cours', 'En cours de livraison'),
        ('livree', 'Livrée'),
        ('annulee', 'Annulée'),
    ]

    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField()
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_livraison = models.DateTimeField(null=True, blank=True)
    generer_recu=models.BooleanField(default=False)

    def __str__(self):
        return f"Commande {self.id} - {self.produit.Nom} - {self.client.Prenom}"    
    
    
    
    
    
    
    
class Facture(models.Model):
    id_Commande = models.ForeignKey(Commande, on_delete=models.CASCADE)
    Date_Facture = models.DateTimeField(auto_now_add=True)
    Montant_Total_Facture = models.DecimalField(max_digits=10, decimal_places=2)
    Informations_Client = models.ForeignKey(Client, on_delete=models.CASCADE)
    Informations_pharmacie = models.ForeignKey(Pharmacie, on_delete=models.CASCADE)
    Nom_Produit = models.CharField(max_length=255)  # Ajoutez le nom du produit
    Quantite_Produit = models.PositiveIntegerField()  # Ajoutez la quantité du produit
    Prix_Unitaire_Produit = models.DecimalField(max_digits=10, decimal_places=2)  # Ajoutez le prix unitaire du produit
    Nom_Pharmacie = models.CharField(max_length=255)  # Ajoutez le nom de la pharmacie
    Nom_Commande = models.CharField(max_length=255)  # Ajoutez le nom de la commande

    STATUT_CHOICES = [
        ('payee', 'Payée'),
        ('en_attente', 'En attente de paiement'),
        # Ajoutez d'autres statuts si nécessaire
    ]
    Statut_Paiement = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')

    def __str__(self):
        return f"Facture {self.id} - Commande {self.id_Commande.produit.Nom}"    
    
    

class Conseil(models.Model):
    titre = models.CharField(max_length=100)
    message = models.TextField()
    pharmacie = models.ForeignKey(Pharmacie, on_delete=models.CASCADE)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titre    