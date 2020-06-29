from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('form_data', views.form_data, name='form_data')
]
