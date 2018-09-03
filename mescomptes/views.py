from django.shortcuts import render
from django.utils.translation import ugettext as _
from django.http import Http404, JsonResponse

from mescomptes.forms import SetCategoriesForm
from mescomptes.models import Inscription, Compte


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


def compte_view(request, compte_nom):
    try:
        compte = Compte.objects.get(name=compte_nom)
    except Compte.DoesNotExist:
        raise Http404(_("This account does not exist"))
    return render(request, 'mescomptes/compte.html', {'compte': compte})


def get_balance_evolution(request, compte_num):
    if request.method == "GET":
        try:
            compte = Compte.objects.get(pk=compte_num)
        except Compte.DoesNotExist:
            raise Http404(_("This account does not exist"))
        data = dict({
            "data": [{
                    "x": [],
                    "y": [],
                    "type": "scatter",
                    "mode": "lines",
                 }],
            "layout": {
                "title": "Evolution de la balance du compte",
                "xaxis": {
                    "type": "date",
                    "rangeselector": {
                        "buttons": [
                            {
                                "count": 1,
                                "label": "1m",
                                "step": "month",
                                "stepmode": "backward",
                            },
                            {
                                "count": 6,
                                "label": "6m",
                                "step": "month",
                                "stepmode": "backward",
                            },
                            {
                                "step": "all",
                            }
                        ]
                    }
                }
            }
        })
        d = data['data'][0]
        d['x'].append(compte.opening_date)
        d['y'].append(compte.opening_balance)
        balance = compte.opening_balance
        query_set = compte.inscription_set.all().order_by('date')
        first_date = compte.opening_date
        last_date = query_set.latest().date
        data['layout']['xaxis']['range'] = [first_date, last_date]
        data['layout']['xaxis']['rangeslider'] = {
            "range":  [first_date, last_date]
        }

        for inscription in query_set:
            if inscription.debit:
                balance = balance - inscription.debit
            if inscription.credit:
                balance = balance + inscription.credit
            d['x'].append(inscription.date)
            d['y'].append(balance)
        return JsonResponse(data)
    else:
        raise Http404(_("Only GET method is allowed"))  # should be http 405 error code
