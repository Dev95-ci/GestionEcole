# utilisateurs/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class Utilisateur(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Administrateur'),
        ('caissier', 'Caissier'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='caissier')
