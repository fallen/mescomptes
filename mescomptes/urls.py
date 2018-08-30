from django.conf.urls import url
from mescomptes.views import index
from mescomptes import views

urlpatterns = [
    url(r'^$', index, name="index"),
    url('^compte/(?P<compte_num>[0-9]*)/get_balance_evolution$', views.get_balance_evolution,
        name="get_balance_evolution"),
    url('^compte/(?P<compte_nom>.*)$', views.compte_view, name="view_compte"),
    url(r'^set_categories$', views.set_categories, name="set_categories")
]
