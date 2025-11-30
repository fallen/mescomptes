from django.shortcuts import render
from django.utils.translation import gettext as _
from django.http import Http404, JsonResponse
from django.db.models.functions import TruncMonth
from django.db.models import Sum

from dateutil.relativedelta import relativedelta

from mescomptes.forms import SetCategoriesForm
from mescomptes.models import Inscription, Compte, Categorie

class MonthReport:
    def __init__(self, inscriptions):
        self.inscriptions = inscriptions
        start_date = inscriptions[0].date
        end_date = inscriptions[-1].date
        self.month = start_date.month
        self.year = start_date.year
        self.date = start_date
        self.categories = {}
        for i in self.inscriptions:
            if i.categorie.exists():
                cats = i.categorie.all()
            else:
                cats = ["Divers"]
            for c in cats:
                if c not in self.categories:
                    self.categories[c] = { 'inscriptions': list(), 'total': 0}
                self.categories[c]['inscriptions'].append(i)
                if i.debit is not None:
                    self.categories[c]['total'] -= i.debit
                if i.credit is not None:
                    self.categories[c]['total'] += i.credit


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

def view_cat(request, compte_nom):
    try:
        compte = Compte.objects.get(name=compte_nom)
    except Compte.DoesNotExist:
        raise Http404(_("This account does not exist"))

    inscriptions = list(Inscription.objects.all())
    first_date = inscriptions[0].date
    last_date = inscriptions[-1].date
    cur_date = first_date
    month_reports = list()
    while True:
        cur_inscriptions = list(Inscription.objects.filter(date__year=cur_date.year, date__month=cur_date.month).all())
        month_report = MonthReport(cur_inscriptions)
        month_reports.append(month_report)
        if cur_date.year == last_date.year and cur_date.month == last_date.month:
            break
        cur_date = cur_date + relativedelta(months=1)

    categories = Categorie.objects.all()
    return render(request, 'mescomptes/view_cat.html', {'compte': compte, 'categories': categories, 'month_reports': month_reports})

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


def get_monthly_debit_evolution(request, compte_num):
    if request.method == "GET":
        try:
            compte = Compte.objects.get(pk=compte_num)
        except Compte.DoesNotExist:
            raise Http404(_("This account does not exist"))
        data = dict({
            "data": [{
                    'x': [],
                    'y': [],
                    "type": "scatter",
                    "mode": "lines",
                 }],
            "layout": {
                "title": "Evolution des débits mensuels",
                "xaxis": {
                    "type": "date",
                    "rangeselector": {
                        "buttons": [
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
        query_set = Inscription.objects.annotate(month=TruncMonth('date')).values('month').\
            annotate(somme=Sum('debit')).order_by('month')
        first_date = query_set.earliest()['month']
        last_date = query_set.latest()['month']
        data['layout']['xaxis']['range'] = [first_date, last_date]
        data['layout']['xaxis']['rangeslider'] = {
            "range":  [first_date, last_date]
        }
        for inscription in query_set:
            d['x'].append(inscription['month'])
            d['y'].append(inscription['somme'])
        return JsonResponse(data)
    else:
        raise Http404(_("Only GET method is allowed"))  # should be http 405 error code
