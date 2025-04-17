from django.db import models
from core.models import Eleve, Classe, AnneeScolaire

class Inscription(models.Model):
    eleve = models.ForeignKey(Eleve, on_delete=models.CASCADE)
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE)
    annee_scolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE)
    frais_inscription = models.DecimalField(max_digits=10, decimal_places=2, default=5000)  # Frais d'inscription (fixes)
    date_inscription = models.DateField(auto_now_add=True)
    
    class Meta:
        unique_together = ('eleve', 'annee_scolaire')  # Un élève ne peut pas être inscrit deux fois pour la même année

    def __str__(self):
        return f"Inscription de {self.eleve.nom} {self.eleve.prenom} en {self.classe.nom} ({self.annee_scolaire.annee})"