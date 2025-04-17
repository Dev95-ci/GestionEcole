from django.urls import path
from . import views

urlpatterns = [
    path('', views.paiement_list, name='paiement_list'),
    path('paiement_eleve/', views.enregistrer_paiement, name='paiement'),
    path('paiement/success/<int:paiement_id>/', views.paiement_success, name='paiement_success'),
    path('recu_inscription/<int:inscription_id>/', views.generer_recu_inscription, name='recu_inscription'),
    path('ajax/montant_restant/', views.montant_restant_ajax, name='montant_restant_ajax'),

]