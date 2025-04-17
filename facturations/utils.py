# utils.py
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from io import BytesIO
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from datetime import date
from django.conf import settings
from num2words import num2words
from reportlab.lib.utils import ImageReader
from django.db.models import Sum






def generer_recu_pdf(paiement):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    largeur, hauteur = letter
    ligne = 20
    y = hauteur - 50

    # Logos et entêtes
    logo_path = os.path.join(settings.BASE_DIR, 'static/img/logo/logo.png')
    if os.path.exists(logo_path):
        c.drawImage(ImageReader(logo_path), 60, y - 40, width=50, height=50)

    c.setFont("Helvetica-Bold", 10)
    c.drawString(120, y, "Ministère de l’Éducation Nationale")
    c.drawString(120, y - 12, "et de l’Alphabétisation")
    c.setFont("Helvetica-Bold", 11)
    c.drawString(120, y - 28, "EPV ROVINESE KAPLEI")
    c.setFont("Helvetica", 9)
    c.drawString(120, y - 40, "SEMER LA LUMIÈRE, RÉCOLTER L’AVENIR")

    c.setFont("Helvetica-Bold", 10)
    c.drawRightString(largeur - 60, y, "REPUBLIQUE DE COTE D’IVOIRE")
    c.drawRightString(largeur - 60, y - 12, "Union - Discipline - Travail")
    c.drawRightString(largeur - 60, y - 28, f"Man, le {date.today().strftime('%d/%m/%Y')}")

    y -= 60
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(largeur / 2, y, "REÇU DE VERSEMENT")
    y -= 30

    # Contenu principal (Année académique et Reçu)
    c.setFont("Helvetica", 11)
    c.drawString(50, y, f"Année académique : {paiement.annee_scolaire.annee}")
    c.drawRightString(largeur - 50, y, f"N° Reçu : REC-{paiement.id:05d}")
    y -= ligne

    # Informations sur l'élève et le paiement
    c.drawString(50, y, f"Nom et prénoms : {paiement.eleve.nom} {paiement.eleve.prenom}")
    c.drawRightString(largeur - 50, y, f"BFF {paiement.montant} Fcfa")
    y -= ligne
    c.drawString(50, y, f"Motif : {paiement.get_type_paiement_display()}")
    y -= ligne
    c.drawString(50, y, f"Classe : {paiement.inscription.classe.nom }")
    y -= ligne
    c.drawString(50, y, f"Matricule : {paiement.eleve.matricule}")
    y -= ligne
    c.drawString(50, y, f"La somme (en lettres) de : {montant_en_lettres(paiement.montant)}")
    y -= ligne * 2
    

    # Règlement du jour (Détails des paiements)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y, "Règlement de ce jour")
    c.drawRightString(largeur - 50, y, f"Total payé à ce jour :")
    y -= ligne

    # Bilan des règlements (Total payé et reste)
    montant_total = paiement.eleve.montant_du or 0
    total_paye = paiement.eleve.paiement_set.filter(
        annee_scolaire=paiement.annee_scolaire,
        type_paiement='scolarite'
    ).aggregate(total=Sum('montant'))['total'] or 0
    reste = montant_total - total_paye

    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y, "Bilan des règlements")
    y -= ligne

    c.setFont("Helvetica", 11)
    c.drawString(50, y, f"Montant scolarité :")
    c.drawRightString(largeur - 50, y, f"{montant_total} Fcfa")
    y -= ligne
    c.drawString(50, y, f"Montant payé :")
    c.drawRightString(largeur - 50, y, f"{paiement.montant} Fcfa")
    y -= ligne
    c.drawString(50, y, f"Total payé à ce jour :")
    c.drawRightString(largeur - 50, y, f"{total_paye} Fcfa")
    y -= ligne
    c.drawString(50, y, f"Reste à payer :")
    c.drawRightString(largeur - 50, y, f"{reste} Fcfa")
    y -= ligne * 2

    # Signature
    c.setFont("Helvetica", 10)
    c.drawString(50, y, f"Caissier (e) : ______________________")
    c.drawRightString(largeur - 50, y, f"Date : {date.today().strftime('%d/%m/%Y')}")
    y -= ligne

    # Finalisation
    c.showPage()
    c.save()
    buffer.seek(0)

    file_name = f"recu_paiement_{paiement.id}.pdf"
    chemin_recu = os.path.join("recus", file_name)
    paiement.recu_pdf.save(chemin_recu, ContentFile(buffer.getvalue()))
    buffer.close()

    return paiement.recu_pdf.url



def montant_en_lettres(montant):
    return num2words(montant, lang='fr').capitalize() + " francs CFA"




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