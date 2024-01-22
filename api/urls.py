from django.urls import path
from .views import (
	ClientRegistrationAPIView,
	UserLoginAPIView,
	ClientViewAPI,
	UserLogoutViewAPI,
 PharmacieRegistrationAPIView
)


urlpatterns = [
	path('client/register/', ClientRegistrationAPIView.as_view()),
	path('client/login/', UserLoginAPIView.as_view()),
	path('client/logout/', UserLogoutViewAPI.as_view()),
 
    path('pharmacie/register/', PharmacieRegistrationAPIView.as_view()),
	path('pharmacie/login/', UserLoginAPIView.as_view()),
	path('pharmacie/logout/', UserLogoutViewAPI.as_view()),
]
