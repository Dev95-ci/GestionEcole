from django.db import models
from core.models import Eleve, Classe, AnneeScolaire
from inscriptions.models import Inscription
from decimal import Decimal
from django.core.exceptions import ValidationError

class Paiement(models.Model):
    eleve = models.ForeignKey(Eleve, on_delete=models.CASCADE)
    montant = models.DecimalField(max_digits=10, decimal_places=2, null=False)  # Montant payé
    date_paiement = models.DateField()
    annee_scolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE)
    statut = models.BooleanField(default=False)  # True = payé, False = non payé
    inscription = models.ForeignKey(Inscription, on_delete=models.CASCADE, null=True, blank=True)  # Lien avec l'inscription
    type_paiement = models.CharField(max_length=50, choices=[('inscription', 'Frais d\'inscription'), ('scolarite', 'Frais de scolarité')])
    recu_pdf = models.FileField(upload_to='recus/', blank=True, null=True)


    def __str__(self):
        return f"Paiement de {self.montant} pour {self.eleve} pour {self.annee_scolaire}"
    
    # def save(self, *args, **kwargs):
    #     if self.type_paiement == "scolarite":
    #         # Recharger l'élève depuis la base pour être sûr de la valeur actuelle
    #         eleve_fresh = Eleve.objects.get(pk=self.eleve.pk)

    #         montant_restant = eleve_fresh.montant_restant
    #         frais_scolarite = eleve_fresh.montant_du

    #         print(f"[DEBUG] Montant restant en base pour {eleve_fresh.nom} : {montant_restant}")
    #         print(f"[DEBUG] Montant à payer : {self.montant}")

    #         if Decimal(self.montant) > montant_restant:
    #             raise ValidationError(
    #                 f"Le montant payé ({self.montant}) dépasse le montant restant ({montant_restant})."
    #             )

    #         # Mettre à jour le montant restant
    #         eleve_fresh.montant_restant -= Decimal(self.montant)

    #         if eleve_fresh.montant_restant <= 0:
    #             self.statut = True
    #             eleve_fresh.montant_restant = Decimal('0.00')

    #         eleve_fresh.save()

    #     super().save(*args, **kwargs)