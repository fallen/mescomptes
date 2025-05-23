from django.urls import re_path
from mescomptes.views import index
from mescomptes import views

urlpatterns = [
    re_path(r'^$', index, name="index"),
    re_path('^compte/(?P<compte_num>[0-9]*)/get_balance_evolution$', views.get_balance_evolution,
    name="get_balance_evolution"),
    re_path('^compte/(?P<compte_num>[0-9]*)/get_monthly_debit_evolution$', views.get_monthly_debit_evolution,
    name="get_monthly_debit_evolution"),
    re_path('^compte/(?P<compte_nom>.*)$', views.compte_view, name="view_compte"),
    re_path(r'^set_categories$', views.set_categories, name="set_categories")
]
