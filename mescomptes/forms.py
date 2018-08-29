from django import forms
from mescomptes.models import Inscription


class SetCategoriesForm(forms.ModelForm):
    class Meta:
        model = Inscription
        fields = ('date', 'libelle', 'credit', 'debit', 'compte')