from django.contrib.auth import login, logout, authenticate
from .forms import UtilisateurForm
from django.contrib import messages
from .models import Utilisateur
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test

# Vérifie si l'utilisateur est admin
def is_admin(user):
    return user.is_authenticated and user.role == 'admin'

def inscription(request):
    if request.method == "POST":
        form = UtilisateurForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UtilisateurForm()
    return render(request, 'utilisateurs/inscription.html', {'form': form})



def connexion(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            print(f"Rôle utilisateur connecté : {user.role}")  # Debug
            if user.role == 'admin':
                return redirect('dashboard')
            elif user.role == 'caissier':
                return redirect('caissier_dashboard')
            else:
                messages.error(request, "Rôle non reconnu.")
                return redirect('login')
        else:
            messages.error(request, 'Nom d’utilisateur ou mot de passe incorrect.')
    return render(request, 'utilisateurs/connexion.html')





def deconnexion(request):
    logout(request)
    return redirect('connexion')


# Vérifie si l'utilisateur est admin
def is_admin(user):
    return user.is_authenticated and user.role == 'admin'

# Liste des utilisateurs
@login_required
@user_passes_test(is_admin)
def liste_utilisateurs(request):
    utilisateurs = Utilisateur.objects.all()
    return render(request, 'utilisateurs/liste_utilisateurs.html', {'utilisateurs': utilisateurs})

# Ajouter un utilisateur
@login_required
@user_passes_test(is_admin)
def ajouter_utilisateur(request):
    if request.method == 'POST':
        form = UtilisateurForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('liste_utilisateurs')
    else:
        form = UtilisateurForm()
    return render(request, 'utilisateurs/utilisateur_form.html', {'form': form, 'form_title': 'Ajouter un utilisateur'})


# Modifier un utilisateur
@login_required
@user_passes_test(is_admin)
def modifier_utilisateur(request, utilisateur_id):
    utilisateur = get_object_or_404(Utilisateur, pk=utilisateur_id)
    if request.method == 'POST':
        form = UtilisateurForm(request.POST, instance=utilisateur)
        if form.is_valid():
            form.save()
            return redirect('liste_utilisateurs')
    else:
        form = UtilisateurForm(instance=utilisateur)
    return render(request, 'utilisateurs/utilisateur_form.html', {'form': form, 'form_title': 'Modifier utilisateur'})


# Supprimer un utilisateur
@login_required
@user_passes_test(is_admin)
def supprimer_utilisateur(request, utilisateur_id):
    utilisateur = get_object_or_404(Utilisateur, pk=utilisateur_id)
    if request.method == 'POST':
        utilisateur.delete()
        return redirect('liste_utilisateurs')
    return render(request, 'utilisateurs/confirm_suppression.html', {'utilisateur': utilisateur})
