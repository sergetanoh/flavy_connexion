from .models import Categorie_Produit, Produit
from .serializers import CategorieProduitSerializer, ProduitSerializer
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework import permissions


class IsSuperUserOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser or request.method in ('GET', 'HEAD', 'OPTIONS')

class IsPharmacieOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_pharmacie==True or request.method in ('GET', 'HEAD', 'OPTIONS')








#############permissions pour commande


class IsClientOrReadOnly(permissions.BasePermission):
    """
    Permission personnalisée pour autoriser uniquement les clients à créer et voir leurs commandes.
    """
    def has_permission(self, request, view):
        if request.method == 'POST':
            # Seuls les clients peuvent passer des commandes
            return request.user.is_pharmacie == False
        elif request.method == 'GET':
            # Les clients peuvent voir leurs propres commandes
            return request.user and request.user.is_authenticated and request.user.is_pharmacie == False
        return False


class IsPharmacieCanModifyCommande(permissions.BasePermission):
    """
    Permission personnalisée pour autoriser uniquement les pharmacies à modifier ou supprimer des commandes.
    """
    def has_object_permission(self, request, view, obj):
        # Seule la pharmacie qui a posté le produit peut modifier ou supprimer la commande
        return request.user and request.user.is_authenticated and request.user.is_pharmacie == True


