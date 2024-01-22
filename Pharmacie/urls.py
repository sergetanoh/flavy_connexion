from django.urls import path
from .views import (
	PharmacieRegistrationAPIView,
	UserLoginAPIView,
	PharmacieViewAPI,
	PharmacieLogoutViewAPI
)


urlpatterns = [
	path('pharmacie/register/', PharmacieRegistrationAPIView.as_view()),
	path('pharmacie/login/', UserLoginAPIView.as_view()),
	
	path('pharmacie/logout/', PharmacieLogoutViewAPI.as_view()),
]
