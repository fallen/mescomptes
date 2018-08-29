from django.shortcuts import render
from django.utils.translation import ugettext as _
from django.http import Http404

from mescomptes.forms import SetCategoriesForm
from mescomptes.models import Inscription


def index(request):
    raise Http404(_("Nothing to see!"))


def set_categories(request):
    ids = request.GET['ids']
    ids = ids.split(',')

    inscriptions = Inscription.objects.filter(id__in=ids)
    if request.method == "GET":
        form = SetCategoriesForm()
    else:
        form = SetCategoriesForm(request.POST)
        if form.is_valid():
            pass
    return render(request, 'mescomptes/set_categories.html', {'form': form})