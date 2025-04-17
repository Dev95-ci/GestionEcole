
from django.http import HttpResponse
from django.template.loader import render_to_string
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.conf import settings
import os
from datetime import date
from core.models import Eleve, Classe, AnneeScolaire
from inscriptions.models import Inscription
from .models import Paiement
from django.shortcuts import render, redirect
from django.utils import timezone
from num2words import num2words
from .utils import generer_recu_pdf
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from reportlab.lib.units import cm
from django.http import JsonResponse
from decimal import Decimal
from django.core.exceptions import ValidationError



def montant_restant_ajax(request):
    eleve_id = request.GET.get('eleve_id')
    try:
        eleve = Eleve.objects.get(id=eleve_id)
        return JsonResponse({'montant_restant': float(eleve.montant_restant)})
    except Eleve.DoesNotExist:
        return JsonResponse({'error': 'Élève introuvable'}, status=404)




@login_required
def paiement_list(request):
    # Récupération de l'année scolaire depuis la requête GET
    annee_scolaire_id = request.GET.get('annee_scolaire')

    # Base queryset : tous les paiements ou filtrés par année
    paiements = Paiement.objects.all().select_related('eleve', 'annee_scolaire')
    if annee_scolaire_id and annee_scolaire_id.isdigit():
        annee_scolaire_id = int(annee_scolaire_id)  # Convertir en entier
        paiements = paiements.filter(annee_scolaire_id=annee_scolaire_id)
    else:
        annee_scolaire_id = None
    # Séparation des paiements par type
    paiements_inscription = paiements.filter(type_paiement='inscription')
    paiements_scolarite = paiements.filter(type_paiement='scolarite')

    # Pagination
    paginator = Paginator(paiements, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Liste des années disponibles
    annees = AnneeScolaire.objects.all()

    # Contexte à passer au template
    context = {
        'page_obj': page_obj,
        'paiements_inscription': paiements_inscription,
        'paiements_scolarite': paiements_scolarite,
        'annees': annees,
        'annee_scolaire_id': annee_scolaire_id,
    }

    return render(request, 'facturations/paiement_list.html', context)



@login_required
def enregistrer_paiement(request):
    if request.method == 'POST':
        try:
            eleve = int(request.POST.get('eleve', ''))
            montant = float(request.POST['montant'])
            date_paiement = request.POST['date_paiement']
            annee_scolaire = int(request.POST.get('annee_scolaire', ''))
            type_paiement = request.POST['type_paiement']
            inscription = request.POST['inscription']
            statut = request.POST['statut']
        
            eleve = Eleve.objects.get(id=eleve)  
            annee_scolaire = AnneeScolaire.objects.get(id=annee_scolaire)
            inscription = Inscription.objects.get(id=inscription)
            #print(inscription.eleve.id)

            paiement = Paiement(
                eleve=eleve,
                montant=montant,
                date_paiement=date_paiement,
                annee_scolaire=annee_scolaire,
                statut=statut,
                type_paiement=type_paiement,
                inscription=inscription
            )
            
            
            montant_restant = eleve.montant_restant
            
            somme_paye = montant
            
            
            if somme_paye < 0 :
                messages.error(request,f"le Montant à payer  doit être supérieur à 0.")
                
            elif montant_restant == 0:
                messages.warning(request, "Cet élève a déjà payé la totalité des frais de scolarité.")
                
            elif somme_paye > montant_restant:
                messages.error(request, f"le Montant à payer  doit être inférieur au montant restant {montant_restant} Fcfa.")
                
            elif somme_paye == montant_restant or somme_paye <= montant_restant or montant_restant != 0:
                montant_restant -= Decimal(somme_paye)
                eleve.montant_restant = montant_restant
                paiement.statut = True
                print(f"le montant restant après paiement est {eleve.montant_restant}")
                eleve.save()
                
                
                paiement.save()
            
            
                generer_recu_pdf(paiement)
            
                return redirect('paiement_success', paiement.id)  # Redirige vers la liste des paiements
            
        except ValidationError as e:
            messages.error(request, e.message)
        
        

        

    context = {
        'eleves': Eleve.objects.all(),
        'annees': AnneeScolaire.objects.all(),
        'inscriptions' : Inscription.objects.all()
    }
    return render(request, 'facturations/effectuer_paiement.html', context)




@login_required
def montant_en_lettres(montant):
    return num2words(montant, lang='fr').capitalize() + " francs CFA"










@login_required
def generer_recu_inscription(inscription, total_paiements):
    nom_fichier = f"recu_inscription_{inscription.id}.pdf"
    chemin_recu = os.path.join(settings.MEDIA_ROOT, 'recus', nom_fichier)
    os.makedirs(os.path.dirname(chemin_recu), exist_ok=True)

    c = canvas.Canvas(chemin_recu, pagesize=A4)
    largeur, hauteur = A4

    # Coordonnées
    x_gauche = 2.5 * cm
    x_droite = 12.5 * cm
    y = hauteur - 3 * cm
    ligne = 1 * cm

    # Titres en haut
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x_gauche, y, "Ministère de l’Éducation Nationale")
    c.drawString(x_gauche, y - 12, "et de l’Alphabétisation")
    c.drawString(x_gauche, y - 28, "EPP MAJOUET ROVINESE KAPLEI")

    c.setFont("Helvetica-Bold", 9)
    c.drawString(x_droite, y, "REPUBLIQUE DE COTE D’IVOIRE")
    c.drawString(x_droite, y - 12, "Union - Discipline - Travail")
    c.drawString(x_droite, y - 28, f"Man, le {date.today().strftime('%d/%m/%Y')}")

    y -= ligne * 2

    # Titre
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(largeur / 2, y, "REÇU DE VERSEMENT")
    y -= ligne

    # Informations principales
    c.setFont("Helvetica", 11)
    c.drawString(x_gauche, y, f"Année académique : {inscription.annee_scolaire}")
    c.drawString(x_droite, y, f"N° Reçu : REC-{inscription.id:05d}")
    y -= ligne

    c.drawString(x_gauche, y, f"Nom et prénoms : {inscription.eleve.nom} {inscription.eleve.prenom}")
    c.drawString(x_droite, y, f"BFF : {inscription.frais_inscription:,.0f} Fcfa")
    y -= ligne

    c.drawString(x_gauche, y, f"Motif : Inscription")
    c.drawString(x_droite, y, f"Classe : {inscription.classe.nom}")
    y -= ligne

    c.drawString(x_gauche, y, f"La somme (en lettres) de : {montant_en_lettres(inscription.montant)}")
    y -= ligne * 1.5

    # Bilan des règlements
    c.setFont("Helvetica-Bold", 11)
    c.drawString(x_gauche, y, "Bilan des règlements")
    c.setFont("Helvetica", 11)
    y -= ligne

    scolarite = inscription.classe.frais_scolarite
    reste = max(scolarite - total_paiements, 0)
    total_paye = total_paiements + inscription.frais_inscription

    c.drawString(x_gauche, y, f"Montant scolarité : {scolarite:,.0f} Fcfa")
    y -= ligne
    c.drawString(x_gauche, y, f"Montant payé : {total_paiements:,.0f} Fcfa")
    y -= ligne
    c.drawString(x_gauche, y, f"Reste à payer : {reste:,.0f} Fcfa")
    y -= ligne * 1.5

    # Règlement du jour
    c.setFont("Helvetica-Bold", 11)
    c.drawString(x_gauche, y, "Règlement de ce jour")
    c.setFont("Helvetica", 11)
    y -= ligne
    c.drawString(x_gauche, y, f"Total payé à ce jour : {total_paye:,.0f} Fcfa")
    y -= ligne * 1.5

    # Signature
    c.drawString(x_gauche, y, f"Caissier (e) (nom et prénoms) : .....................................................")
    c.drawString(x_droite, y, f"Date : {inscription.date_inscription.strftime('%d/%m/%Y')}")

    c.save()

    return os.path.join('recus', nom_fichier)





@login_required
def paiement_success(request, paiement_id):
    # Récupérer l'objet Paiement à partir de l'ID passé dans l'URL
    paiement = get_object_or_404(Paiement, id=paiement_id)

    # Vérifier si le paiement a bien été effectué
    if paiement.statut:
        # Ajouter un message de succès
        messages.success(request, "Le paiement a été effectué avec succès.")

        # Passer les données nécessaires au template
        context = {
            'paiement': paiement,
            'eleve': paiement.eleve,
            'montant_restant': paiement.eleve.montant_restant,
            'recu_pdf': paiement.recu_pdf.url if paiement.recu_pdf else None
        }
        return render(request, 'facturations/paiement_success.html', context)

    else:
        # Si le paiement n'est pas validé, rediriger ou afficher un message d'erreur
        messages.error(request, "Le paiement n'a pas été validé.")
        return HttpResponse("Paiement non validé.")
