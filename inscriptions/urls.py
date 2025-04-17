from django.urls import path
from . import views

urlpatterns = [
    path('', views.inscrire_eleve, name='inscription_form'),
    path('success/', views.inscription_success, name='inscription_success'),
]
