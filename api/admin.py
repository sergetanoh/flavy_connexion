from django.contrib import admin
from .models import (
    User, Client, Pharmacie, Recherche, Commande, Conseil,
    Notification, Invoice, InvoiceItem, InvoicePayment, WalletPharmacie, WalletPharmacieHistory
)

# Actions pour activer/désactiver les objets
def activer_objets(modeladmin, request, queryset):
    queryset.update(est_actif=True)
activer_objets.short_description = "Activer les objets sélectionnés"

def desactiver_objets(modeladmin, request, queryset):
    queryset.update(est_actif=False)
desactiver_objets.short_description = "Désactiver les objets sélectionnés"

# Admin pour le modèle User
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'is_active', 'is_staff', 'is_pharmacie', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'is_pharmacie', 'date_joined')
    search_fields = ('email', 'username')
    actions = [activer_objets, desactiver_objets]

# Admin pour le modèle Client
@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prenom', 'sexe', 'ville', 'phone', 'est_actif', 'date_creation')
    list_filter = ('sexe', 'est_actif', 'date_creation')
    search_fields = ('nom', 'prenom', 'phone')
    actions = [activer_objets, desactiver_objets]

# Admin pour le modèle Pharmacie
@admin.register(Pharmacie)
class PharmacieAdmin(admin.ModelAdmin):
    list_display = ('nom_pharmacie', 'ville_pharmacie', 'numero_contact_pharmacie', 'degarde', 'est_actif', 'date_creation')
    list_filter = ('degarde', 'est_actif', 'ville_pharmacie')
    search_fields = ('nom_pharmacie', 'numero_contact_pharmacie')
    actions = [activer_objets, desactiver_objets]

# Admin pour le modèle Recherche
@admin.register(Recherche)
class RechercheAdmin(admin.ModelAdmin):
    list_display = ('client', 'nom_medicament', 'quantite', 'statut', 'date_creation')
    list_filter = ('statut', 'en_attente', 'terminer', 'est_actif')
    search_fields = ('nom_medicament', 'client__nom', 'client__prenom')
    actions = [activer_objets, desactiver_objets]

# Admin pour le modèle Commande
@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'nom_medicament', 'quantite', 'statut', 'date_creation', 'date_livraison')
    list_filter = ('statut', 'en_attente', 'terminer', 'est_actif')
    search_fields = ('client__nom', 'client__prenom', 'nom_medicament')
    actions = [activer_objets, desactiver_objets]

# Admin pour le modèle Conseil
@admin.register(Conseil)
class ConseilAdmin(admin.ModelAdmin):
    list_display = ('titre', 'pharmacie', 'est_actif', 'date_creation')
    list_filter = ('est_actif',)
    search_fields = ('titre', 'pharmacie__nom_pharmacie')
    actions = [activer_objets, desactiver_objets]

# Admin pour le modèle Notification
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user_type', 'is_read', 'est_actif', 'date_creation')
    list_filter = ('user_type', 'is_read', 'est_actif')
    search_fields = ('title', 'message')
    actions = [activer_objets, desactiver_objets]

# Admin pour le modèle Invoice
@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'status', 'total_amount', 'total', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('client__nom', 'client__prenom', 'reference')
    actions = [activer_objets, desactiver_objets]

# Admin pour le modèle InvoiceItem
@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'description', 'quantity', 'unit_price')
    search_fields = ('invoice__reference', 'description')

# Admin pour le modèle InvoicePayment
@admin.register(InvoicePayment)
class InvoicePaymentAdmin(admin.ModelAdmin):
    list_display = ('reference', 'invoice', 'status', 'amount_total', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('reference', 'invoice__reference')

# Admin pour le modèle WalletPharmacie
@admin.register(WalletPharmacie)
class WalletPharmacieAdmin(admin.ModelAdmin):
    list_display = ('pharmacie', 'balance', 'old_balance', 'created_at')
    search_fields = ('pharmacie__nom_pharmacie',)

# Admin pour le modèle WalletPharmacieHistory
@admin.register(WalletPharmacieHistory)
class WalletPharmacieHistoryAdmin(admin.ModelAdmin):
    list_display = ('wallet', 'action_type', 'amount', 'new_balance', 'created_at')
    list_filter = ('action_type', 'created_at')
    search_fields = ('wallet__pharmacie__nom_pharmacie', 'label')
