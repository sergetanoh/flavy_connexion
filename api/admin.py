from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import *

# Personnalisez l'affichage dans l'interface d'administration pour les modèles spécifiques

class ClientAdmin(admin.ModelAdmin):
    list_display = ('user', 'prenom', 'adresse', 'ville', 'phone', 'sexe')
    search_fields = ('user__email', 'prenom', 'phone')

class PharmacieAdmin(admin.ModelAdmin):
    list_display = ('user', 'num_pharmacie', 'nom_pharmacie', 'adresse_pharmacie', 'ville_pharmacie', 'numero_contact_pharmacie','degarde')
    search_fields = ('user__email', 'nom_pharmacie', 'num_pharmacie','degarde')


    def get_pharmacie_name(self, obj):
        if obj.Id_Pharmacie.user.is_pharmacie:  # Assurez-vous que le champ correct est utilisé ici
            return obj.Id_Pharmacie.nom_pharmacie if obj.Id_Pharmacie.user else None
        else:
            return "Non applicable"
    
    get_pharmacie_name.short_description = 'Nom de la Pharmacie'



class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'is_active', 'is_staff', 'date_joined', 'is_pharmacie')
    search_fields = ('email', 'username')

# Enregistrez les modèles avec leurs classes d'administration personnalisées

admin.site.register(User, UserAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(Pharmacie, PharmacieAdmin)
admin.site.register(Commande)
admin.site.register(Conseil)
