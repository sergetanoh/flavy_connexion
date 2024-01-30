from django.urls import path
from .views import (
	ClientRegistrationAPIView,
	UserLoginAPIView,
	
	UserLogoutViewAPI,
 PharmacieRegistrationAPIView,
 ProduitAPIView,
 CategorieProduitAPIView,
CommandeAPIViewPharmacie,
CommandeAPIViewClient,
CommandeDetailView
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)


urlpatterns = [
	path('client/register/', ClientRegistrationAPIView.as_view()),
	path('client/login/', UserLoginAPIView.as_view()),
	path('client/logout/', UserLogoutViewAPI.as_view()),
	path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
 
 
    path('pharmacie/register/', PharmacieRegistrationAPIView.as_view()),
	path('pharmacie/login/', UserLoginAPIView.as_view()),
	path('pharmacie/logout/', UserLogoutViewAPI.as_view()),
 
 
 #################   
 path('api/categories/', CategorieProduitAPIView.as_view(), name='categorie_produit_list'),
    path('api/categories/<int:pk>/', CategorieProduitAPIView.as_view(), name='categorie_produit_detail'),

    # Produits
    path('api/products/', ProduitAPIView.as_view(), name='produit_list'),
    path('api/products/<int:pk>/', ProduitAPIView.as_view(), name='produit_detail'),
    
    #commande
    path('api/commande/pharmacie', CommandeAPIViewPharmacie.as_view(), name='commande_pharmacie'),
    path('api/commande/client', CommandeAPIViewClient.as_view(), name='commande_client'),
    
    path('api/commande/client/detail/', CommandeDetailView.as_view(), name='commande_client_detail'),
    
]
