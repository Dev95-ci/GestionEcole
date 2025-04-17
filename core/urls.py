# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('caissier/dashboard/', views.caissier_dashboard, name='caissier_dashboard'),
    path('export/pdf/', views.dashboard_export_pdf, name='dashboard_export_pdf'),
    path('export/excel/', views.dashboard_export_excel, name='dashboard_export_excel'),
    path('eleves/', views.liste_eleves, name='liste_eleves'),
    path('eleves/ajouter/', views.ajout_eleve, name='ajout_eleve'),
    path('eleves/<int:id>/modifier/', views.modifier_eleve ,name='modifier_eleve'),
    path('eleve/<int:eleve_id>/details', views.details_eleve, name='details_eleve'),
    path('get_paiement_details/<int:paiement_id>/', views.paiement_details, name='paiement_details'),
    
    
    
    
    path('classes/', views.liste_classes, name='liste_classes'),
    path('classes/ajouter/', views.ajout_classe, name='ajout_classe'),
    path('classes/<int:id>/modifier/', views.modifier_classe ,name='modifier_classe'),
    path('classes/<int:id>/supprimer/',views.supprimer_classe ,name='supprimer_classe'),
    path('classes/<int:classe_id>/details',views.details_classe,name='details_classe'),
    
    
    
    
    
    
    path('annees/', views.liste_annees, name='liste_annees'),
    path('annees/ajouter/', views.ajout_annee, name='ajout_annee'),
]
