from django.contrib import admin
from django.http import HttpResponseRedirect
from django.utils.translation import gettext as _

from mescomptes.models import Compte, Inscription, Devise, Categorie, Regex


@admin.register(Compte)
class CompteAdmin(admin.ModelAdmin):
    pass


def set_categories(modeladmin, request, queryset):
    selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
    return HttpResponseRedirect('/comptes/set_categories?ids={}'.format(','.join(selected)))


set_categories.short_description = _("Set categories")


@admin.register(Inscription)
class InscriptionAdmin(admin.ModelAdmin):
    list_display = ('date', 'libelle', 'credit', 'debit', 'compte', 'categories')
    search_fields = ('date', 'libelle', 'credit', 'debit')
    list_filter = ('date', 'compte')
    list_display_links = ('libelle', )
    actions = [set_categories]

    def categories(self, inscription):
        cats = ""
        for categorie in inscription.categorie.all():
            cats = cats + ", {}".format(categorie)
        return cats


@admin.register(Devise)
class DeviseAdmin(admin.ModelAdmin):
    pass


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    pass

@admin.register(Regex)
class RegexAdmin(admin.ModelAdmin):
    pass
