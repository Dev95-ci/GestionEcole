# core/views.py
from django.shortcuts import get_object_or_404, render, redirect
from .models import Eleve, AnneeScolaire, Classe
from .forms import EleveForm, ClasseForm,AnneeScolaireForm
from facturations.models import Paiement
from inscriptions.models import Inscription
from django.contrib import messages
from django.db.models import Count,Sum,F,Q
from django.db.models.functions import TruncMonth
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
import openpyxl
from openpyxl.utils import get_column_letter
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator


def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == 'admin':
            return view_func(request, *args, **kwargs)
        return redirect('connexion')
    return wrapper

def caissier_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == 'caissier':
            return view_func(request, *args, **kwargs)
        return redirect('connexion')
    return wrapper



@admin_required
@login_required
def dashboard_export_excel(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Élèves par classe"

    # En-têtes
    ws.append(["Classe", "Nombre d'élèves"])

    data = (
        Inscription.objects.values('classe__nom')
        .annotate(total=Count('id'))
    )

    for item in data:
        ws.append([item['classe__nom'], item['total']])

    response = HttpResponse(content_type="application/ms-excel")
    response['Content-Disposition'] = 'attachment; filename="dashboard.xlsx"'
    wb.save(response)
    return response


@admin_required
@login_required
def dashboard_export_pdf(request):
    inscriptions = Inscription.objects.values('classe__nom').annotate(total=Count('id'))

    template_path = 'dashboard_pdf.html'
    context = {'inscriptions': inscriptions}
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="dashboard.pdf"'
    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Erreur lors de la génération du PDF')
    return response




@login_required
def caissier_dashboard(request):
    
    return render(request, 'caissier_dashboard.html')





@admin_required
@login_required
def dashboard(request):
    # Filtres reçus
    selected_annee = request.GET.get('annee')
    selected_classe = request.GET.get('classe')
    # Calcul du total des frais d'inscription
    total_frais_inscription = Paiement.objects.filter(type_paiement='inscription').aggregate(Sum('montant'))['montant__sum'] or 0

    # Calcul du total des frais de scolarité
    total_frais_scolarite = Paiement.objects.filter(type_paiement='scolarite').aggregate(Sum('montant'))['montant__sum'] or 0

    # Calcul du total général des paiements (inscription + scolarité)
    total_paiements = Paiement.objects.aggregate(Sum('montant'))['montant__sum'] or 0

    inscriptions = Inscription.objects.all()

    if selected_annee:
        inscriptions = inscriptions.filter(annee_scolaire__id=selected_annee)
    if selected_classe:
        inscriptions = inscriptions.filter(classe__id=selected_classe)

    # Résumés
    total_eleves = inscriptions.values('eleve').distinct().count()
    total_classes = Classe.objects.count()
    total_paiements = Paiement.objects.aggregate(total=Sum('montant'))['total'] or 0

    # Graphiques
    chart_data_classes = inscriptions.values('classe__nom').annotate(total=Count('id'))
    chart_data_classes = [{'label': x['classe__nom'], 'value': x['total']} for x in chart_data_classes]

    paiements = (
        Paiement.objects.annotate(month=TruncMonth('date_paiement'))
        .values('month')
        .annotate(total=Sum('montant'))
        .order_by('month')
    )
    chart_data_paiements = [{'label': p['month'].strftime('%B %Y'), 'value': float(p['total'])} for p in paiements]

    chart_data_annees = inscriptions.values('annee_scolaire__annee').annotate(total=Count('id'))
    chart_data_annees = [{'label': a['annee_scolaire__annee'], 'value': a['total']} for a in chart_data_annees]

    # Données pour les filtres
    annees = AnneeScolaire.objects.all()
    classes = Classe.objects.all()
    
    # Liste des classes avec paiements et restants
    paiements_par_classe = Classe.objects.annotate(
    total_frais=Sum('inscription__classe__frais_scolaire'),
    total_paye=Sum(
        'inscription__eleve__paiement__montant',
        filter=Q(inscription__eleve__paiement__type_paiement='scolarite')
    )
    ).annotate(
        total_restant=F('total_frais') - F('total_paye')
    )


    return render(request, 'dashboard.html', {
        'total_eleves': total_eleves,
        'total_classes': total_classes,
        'total_paiements': total_paiements,
        'chart_data_classes': chart_data_classes,
        'chart_data_paiements': chart_data_paiements,
        'chart_data_annees': chart_data_annees,
        'annees': annees,
        'classes': classes,
        'selected_annee': selected_annee,
        'selected_classe': selected_classe,
        'total_frais_inscription': total_frais_inscription,
        'total_frais_scolarite': total_frais_scolarite,
        'total_paiements': total_paiements,
        'paiements_par_classe': paiements_par_classe,
    })



    
    
    
    
    
@login_required  

def liste_eleves(request):
    query = request.GET.get('q', '')
    eleves = Eleve.objects.all()

    if query:
        # Recherche par nom, prénom, classe ou année scolaire
        eleves = eleves.filter(
            Q(nom__icontains=query) | 
            Q(prenom__icontains=query)
        )

    # Pagination
    paginator = Paginator(eleves, 30)  # 10 élèves par page
    page_number = request.GET.get('page')  # Récupère la page demandée dans l'URL
    page_obj = paginator.get_page(page_number)

    return render(request, 'eleves/liste_eleves.html', {'page_obj': page_obj, 'query': query})



@admin_required
@login_required
def ajout_eleve(request):
    if request.method == 'POST':
        form = EleveForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('liste_eleves')
    else:
        form = EleveForm()
    return render(request, 'eleves/ajout_eleve.html', {'form': form})


@admin_required
@login_required
def modifier_eleve(request, id):
    eleve = get_object_or_404(Eleve, id=id)
    if request.method == "POST":
        form = EleveForm(request.POST, instance=eleve)
        if form.is_valid():
            form.save()
            messages.success(request, "l'eleve à été modifié avec succès")
            return redirect("liste_eleves")
    else:
        form = EleveForm(instance=eleve)
    return render(request, "eleves/modifier_eleve.html", {"form": form, 'eleve':eleve})




@login_required
def details_eleve(request, eleve_id):
    # Récupérer l'élève par son ID
    eleve = get_object_or_404(Eleve, id=eleve_id)

    # Récupérer les inscriptions de l'élève
    inscriptions = Inscription.objects.filter(eleve=eleve)

    # Récupérer les paiements associés à chaque inscription
    paiements = Paiement.objects.filter(eleve=eleve)

    context = {
        'eleve': eleve,
        'inscriptions': inscriptions,
        'paiements': paiements,
    }

    return render(request, 'eleves/details_eleve.html', context)





@login_required
def paiement_details(request, paiement_id):
    paiement = Paiement.objects.get(id=paiement_id)

    # Retourner les détails du paiement sous forme de JSON
    data = {
        'montant': paiement.montant,
        'date_paiement': paiement.date_paiement,
        'type_paiement': paiement.get_type_paiement_display(),
        'statut': paiement.statut,
    }
    return JsonResponse(data)




# la logique pour la gestion des classes
@admin_required
@login_required
def liste_classes(request):
    query = request.GET.get('q', '')
    classes = Classe.objects.all()

    if query:
        classes = classes.filter(Q(nom__icontains=query))

    return render(request, 'classes/liste_classes.html', {'classes': classes, 'query': query})




@admin_required
@login_required
def ajout_classe(request):
    if request.method == 'POST':
        form = ClasseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "la classe à été ajoutée avec succès")
            return redirect('liste_classes')
    else:
        form = ClasseForm()
    return render(request, 'classes/ajout_classe.html', {'form': form})



@admin_required
@login_required
def modifier_classe(request, id):
    classe = get_object_or_404(Classe, id=id)
    if request.method == "POST":
        form = ClasseForm(request.POST, instance=classe)
        if form.is_valid():
            form.save()
            messages.success(request, "la classe à été modifiée avec succès")
            return redirect("liste_classes")
    else:
        form = ClasseForm(instance=classe)
    return render(request, "classes/modifier_classe.html", {"form": form, 'classe':classe})



@admin_required
@login_required
def supprimer_classe(request, id):
    classe = get_object_or_404(Classe, id=id)
    if request.method == "POST":
        classe.delete()
        messages.success(request, "la classe à été supprimer avec succès")
        return redirect("liste_classes")
    return render(request, "classes/supprimer_classe.html", {"classe": classe})



@admin_required
@login_required
def details_classe(request, classe_id):
    try:
        # Récupérer la classe par son ID
        classe = Classe.objects.get(id=classe_id)
        
        # Récupérer tous les élèves inscrits dans cette classe
        inscriptions = Inscription.objects.filter(classe=classe)
        
        # Créer une liste pour afficher les paiements associés à chaque élève
        eleves_paiements = []
        for inscription in inscriptions:
            paiements = Paiement.objects.filter(inscription=inscription)
            eleves_paiements.append({
                'eleve': inscription.eleve,
                'paiements': paiements
            })
        
        context = {
            'classe': classe,
            'inscriptions': inscriptions,
            'eleves_paiements': eleves_paiements,
        }
        return render(request, 'classes/details_classe.html', context)
    except Classe.DoesNotExist:
        # Si la classe n'existe pas, rediriger ou afficher une erreur
        return render(request, 'classe/error.html', {'message': 'Classe non trouvée'}) 





# la logique pour la gestion des années scolaire
@admin_required
@login_required
def liste_annees(request):
    query = request.GET.get('q', '')
    annees = AnneeScolaire.objects.all()

    if query:
        annees = annees.filter(
            Q(annee__contains=query) | Q(date_fin__contains=query)
        )

    return render(request, 'annee/liste_annee.html', {'annees': annees, 'query': query})


@login_required
@admin_required
def ajout_annee(request):
    if request.method == 'POST':
        form = AnneeScolaireForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "l'annéé à été ajoutée avec succès")
            return redirect('liste_annees')
    else:
        form = AnneeScolaireForm()
    return render(request, 'annee/ajout_annee.html', {'form': form})
