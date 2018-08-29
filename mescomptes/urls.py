from django.conf.urls import url
from mescomptes.views import index
from mescomptes import views

urlpatterns = [
    url(r'^$', index, name="index"),
    url(r'^set_categories$', views.set_categories, name="set_categories")
]
