
from django.shortcuts import render, redirect
from django.contrib import messages
from core.models import Eleve, Classe, AnneeScolaire
from datetime import datetime
from facturations.models import Paiement
from .models import Inscription
from decimal import Decimal


def inscrire_eleve(request):
    context = {
        'classes': Classe.objects.all(),
        'annees': AnneeScolaire.objects.filter(est_active=True)
    }

    if request.method == 'POST':
        nom = request.POST.get('nom', '')
        prenom = request.POST.get('prenom', '')
        date_naissance = request.POST.get('date_naissance', '')
        phone = request.POST.get('phone', '')
        annee_scolaire_id = request.POST.get('annee_scolaire', '')
        classe_id = request.POST.get('classe', '')
        montant_paye = request.POST.get('montant_paye', '')
        date_paiement = request.POST.get('date_paiement', '')

        # Remplir le formulaire avec les valeurs précédemment saisies
        context['saisie'] = {
            'nom': nom,
            'prenom': prenom,
            'date_naissance': date_naissance,
            'annee_scolaire': annee_scolaire_id,
            'classe': classe_id,
            'montant_paye': montant_paye,
            'date_paiement': date_paiement,
            'phone': phone,
        }

        # Vérifier si l'élève est déjà inscrit pour l'année scolaire
        # if Inscription.objects.filter(eleve__nom=nom, eleve__prenom=prenom, annee_scolaire_id=annee_scolaire_id).exists():
        #     messages.error(request, "Cet élève est déjà inscrit pour cette année scolaire.")
        #     return render(request, 'inscriptions/inscription.html', context)

        if 'payer_frais_inscription' in request.POST:
            try:
                montant_paye = float(montant_paye)
            except ValueError:
                messages.error(request, "Montant invalide.")
                return render(request, 'inscriptions/inscription.html', context)

            classe = Classe.objects.get(pk=classe_id)
            frais_inscription = classe.frais_inscription  # frais d'inscription fixes
            frais_scolaire = classe.frais_scolaire

            if montant_paye == frais_inscription:
                try:
                    # Conversion de la date de naissance et de la date de paiement
                    date_naissance_obj = datetime.strptime(date_naissance, '%Y-%m-%d').date()
                    date_paiement_obj = datetime.strptime(date_paiement, '%Y-%m-%d').date()

                    # Créer l'élève
                    eleve = Eleve.objects.create(
                        nom=nom,
                        prenom=prenom,
                        date_naissance=date_naissance_obj,
                        telephone=phone,
                        montant_du=frais_scolaire,
                        montant_restant=frais_scolaire  # Initialiser le montant restant
                    )

                    # Générer le matricule automatiquement
                    eleve.matricule = eleve.generate_matricule()
                    eleve.save()

                    # Récupérer l'année scolaire et la classe
                    annee_scolaire = AnneeScolaire.objects.get(id=annee_scolaire_id)
                    classe = Classe.objects.get(id=classe_id)

                    # Créer l'inscription de l'élève
                    inscription = Inscription.objects.create(
                        eleve=eleve,
                        classe=classe,
                        annee_scolaire=annee_scolaire,
                        frais_inscription=frais_inscription
                    )

                    # Enregistrer le paiement
                    Paiement.objects.create(
                        eleve=eleve,
                        montant=montant_paye,
                        annee_scolaire=annee_scolaire,
                        statut=True,
                        inscription=inscription,
                        type_paiement='inscription',
                        date_paiement=date_paiement_obj
                    )

                    # Mettre à jour le montant restant de l'élève
                    eleve.montant_restant -= Decimal(montant_paye)
                    eleve.save()

                    messages.success(request, f"L'élève {nom} {prenom} a été inscrit avec succès. Matricule : {eleve.matricule}")
                    return redirect('inscription_success')
            
                except ValueError:
                    messages.error(request, "Date de naissance ou date de paiement invalide.")
                    return render(request, 'inscriptions/inscription.html', context)
             
            elif  montant_paye > frais_inscription:
                messages.error(request, f"Le montant payé {montant_paye} est supérieur au frais d'inscription de la classe qui est de {frais_inscription}")
                
            else:
                manque = frais_inscription - Decimal(montant_paye)
                messages.error(request, f"Le montant payé est insuffisant. Il manque {manque} FCFA.")
        else:
            messages.error(request, "Le paiement des frais d'inscription est obligatoire.")

    return render(request, 'inscriptions/inscription.html', context)


def inscription_success(request):
    return render(request, 'inscriptions/inscription_success.html')