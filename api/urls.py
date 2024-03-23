from django.urls import path
from .views import (
	ClientRegistrationAPIView,
    ClientUpdateAPIView,
	UserLoginAPIView,
	
	UserLogoutViewAPI,
    PharmacieRegistrationAPIView,
    PharmacieUpdateAPIView,

    UserDetailView,
    get_pharmacie,
    GetPharmacieGarde,
    PasserCommandeClient,
    GestionCommandeDetailClient,
    PharmacieDetail,
    CommandesPharmacietous,
    ConseilDetail,
    get_Conseil,
    
    RechercheList,
    RechercheDetail,
    UserByTokenViewAPI,
    
    NotificationList, 
    NotificationDetail
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
	path('client/update/', ClientUpdateAPIView.as_view()),
	 
	path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('auth/get-user/by-token/', UserByTokenViewAPI.as_view()),
 
    path('pharmacie/register/', PharmacieRegistrationAPIView.as_view()),
	path('pharmacie/login/', UserLoginAPIView.as_view()),
	path('pharmacie/logout/', UserLogoutViewAPI.as_view()),
	path('pharmacie/update/', PharmacieUpdateAPIView.as_view()),
 
    #################   COMMANDES #################
    # URL pour gérer une commande spécifique pour le client
    path('clients/commandes/', PasserCommandeClient.as_view(), name='passer_commande_client'),
    path('clients/commandes/<int:pk>/', GestionCommandeDetailClient.as_view(), name='gestion_commande_detail_client'),
    
    # URL pour obtenir les détails d'une commande d'une pharmacie spécifique
    path('pharmacies/commandes/<int:pk>/', PharmacieDetail.as_view(), name='pharmacie_detail'),
    path('pharmacies/commandes/', CommandesPharmacietous.as_view(), name='commandes_pharmacie_tous'),
    
    path('user/profile',UserDetailView.as_view(), name='user_profile'),
    path("get-pharmacie/", get_pharmacie.as_view(), name="get_pharmacie"),
    path("get-pharmacie-garde/", GetPharmacieGarde.as_view(), name="get_pharmaciegarde"),

    path('conseils/', ConseilDetail.as_view(), name='conseil_create'),
    path('conseils/all', get_Conseil.as_view(), name='conseil_get_all'),
    path('conseils/<int:pk>/', ConseilDetail.as_view(), name='conseil_detail'),

    path('recherches/', RechercheList.as_view(), name='recherche-list'),
    path('recherches/<int:pk>/', RechercheDetail.as_view(), name='recherche-detail'),
    
    path('notifications/', NotificationList.as_view(), name='notification-list'),
    path('notifications/<int:pk>/', NotificationDetail.as_view(), name='Notification-detail'),
]
 
