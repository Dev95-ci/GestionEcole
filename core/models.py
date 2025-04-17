from django.db import models
from random import random
from datetime import datetime
from django.dispatch import receiver
import random



class Eleve(models.Model):
    nom = models.CharField(max_length=255)
    prenom = models.CharField(max_length=255)
    date_naissance = models.DateField()
    matricule = models.CharField(max_length=50, unique=True, blank=True, null=True)
    telephone = models.CharField(max_length=15, blank=True, null=True)
    
    montant_du = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0)
    # montant_restant = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0)
    montant_restant = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Montant restant à payer
    
    def __str__(self):
        return f"{self.nom} {self.prenom} - {self.matricule}"


    def generate_matricule(self):
        annee_scolaire = str(self.date_naissance.year)  # Par exemple, baser le matricule sur l'année de naissance
        nom_code = self.nom[:2].upper()  # Utiliser les deux premières lettres de la classe (par exemple, "CP")
        random_code = random.randint(100, 999)  # Générer un code aléatoire à trois chiffres
        return f"{annee_scolaire}{nom_code}{random_code}"
    
    def initialiser_montants(self, montant):
        """
            montant_restant lors de l'inscription.
        """
        if montant < 0:
            raise ValueError("Le montant total ne peut pas être négatif.")
        
        self.montant_restant = montant
        return self.montant_restant
        
        
        

    # Signal pour générer le matricule avant la sauvegarde
from django.db.models.signals import pre_save
from django.dispatch import receiver

@receiver(pre_save, sender=Eleve)
def set_matricule(sender, instance, **kwargs):
    if not instance.matricule:  # Si aucun matricule n'est spécifié
        instance.matricule = instance.generate_matricule()


class Classe(models.Model):
    nom = models.CharField(max_length=255)
    frais_scolaire = models.DecimalField(max_digits=10, decimal_places=2)  # Montant des frais de scolarité
    frais_inscription = models.DecimalField(max_digits=10, decimal_places=2) # Montant des frais d'inscription

    def __str__(self):
        return f"{self.nom} - Frais d'inscription {self.frais_inscription} - Frais de scolarité :{self.frais_scolaire} Fcfa"
    

# Modèle pour l'année scolaire
class AnneeScolaire(models.Model):
    annee = models.CharField(max_length=9, unique=True)  # Exemple : "2024-2025"
    date_debut = models.DateField()
    date_fin = models.DateField()
    est_active = models.BooleanField(default=True)

    def __str__(self):
        return self.annee