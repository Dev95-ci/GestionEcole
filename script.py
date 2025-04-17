from django.db import models



class Inscription(models.Model):
    eleve = models.ForeignKey(Eleve, on_delete=models.CASCADE)
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE)
    annee_scolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE)
    frais_inscription = models.DecimalField(max_digits=10, decimal_places=2, default=5000)  # Frais d'inscription (fixes)
    date_inscription = models.DateField(auto_now_add=True)
    # recu_pdf = models.FileField(upload_to='recus/', blank=True, null=True)

    class Meta:
        unique_together = ('eleve', 'annee_scolaire')  # Un élève ne peut pas être inscrit deux fois pour la même année

    def __str__(self):
        return f"Inscription de {self.eleve.nom} {self.eleve.prenom} en {self.classe.nom} ({self.annee_scolaire.annee})"
    
class Paiement(models.Model):
    eleve = models.ForeignKey(Eleve, on_delete=models.CASCADE)
    montant = models.DecimalField(max_digits=10, decimal_places=2)  # Montant payé
    date_paiement = models.DateField()
    annee_scolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE)
    statut = models.BooleanField(default=False)  # True = payé, False = non payé
    inscription = models.ForeignKey(Inscription, on_delete=models.CASCADE, null=True, blank=True)  # Lien avec l'inscription
    type_paiement = models.CharField(max_length=50, choices=[('inscription', 'Frais d\'inscription'), ('scolarite', 'Frais de scolarité')])

    def __str__(self):
        return f"Paiement de {self.montant} pour {self.eleve} pour {self.annee_scolaire}"
    

class Eleve(models.Model):
    nom = models.CharField(max_length=255)
    prenom = models.CharField(max_length=255)
    date_naissance = models.DateField()
    
    def __str__(self):
        return f"{self.nom} {self.prenom}"


class Classe(models.Model):
    nom = models.CharField(max_length=255)
    frais_scolaire = models.DecimalField(max_digits=10, decimal_places=2)  # Montant des frais de scolarité

    def __str__(self):
        return self.nom
    

# Modèle pour l'année scolaire
class AnneeScolaire(models.Model):
    annee = models.CharField(max_length=9, unique=True)  # Exemple : "2024-2025"
    date_debut = models.DateField()
    date_fin = models.DateField()
    est_active = models.BooleanField(default=True)

    def __str__(self):
        return self.annee