from django import forms
from .models import Eleve, Classe, AnneeScolaire

class EleveForm(forms.ModelForm):
    class Meta:
        model = Eleve
        fields = ['nom', 'prenom', 'date_naissance', "telephone"]
        widgets = {
            "nom" : forms.TextInput(attrs={
                "class" : "form-control",
            }),
            "prenom" : forms.TextInput(attrs={
                "class" : "form-control",
            }),
            "telephone" : forms.TextInput(attrs={
                "class" : "form-control",
            }),
            "date_naissance" : forms.DateInput(attrs={"class":"form-control"})
        }
        
        
        
        
class ClasseForm(forms.ModelForm):
    class Meta:
        model = Classe
        fields = ("nom", "frais_scolaire", "frais_inscription")
        widgets = {
            "nom" : forms.TextInput(attrs={
                "class" : "form-control",
            }),
            "frais_scolaire" : forms.TextInput(attrs={
                "class" : "form-control",
            }),
            "frais_inscription" : forms.TextInput(attrs={
                "class" : "form-control",
            })
        }
        
        
class AnneeScolaireForm(forms.ModelForm):
    class Meta:
        model = AnneeScolaire
        fields = ["annee", "date_debut", "date_fin", "est_active"]
        widgets = {
            "annee" : forms.TextInput(attrs={
                "class" : "form-control",
            }),
            "est_active" : forms.CheckboxInput(attrs={
                "class" : "form-control",
                "type":"checkbox",
            }),
            "date_debut" : forms.DateInput(attrs={
                "class" : "form-control",
                "type":"date",
            }),
            "date_fin" : forms.DateInput(attrs={
                "class" : "form-control",
                "type":"date",
            })
        }
        