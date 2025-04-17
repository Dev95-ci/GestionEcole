# core/admin.py
from django.contrib import admin
from .models import Classe, AnneeScolaire, Eleve

    

admin.site.register(Classe)
admin.site.register(AnneeScolaire)
admin.site.register(Eleve)

