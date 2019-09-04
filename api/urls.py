from django.urls import path


from . import views


urlpatterns = [
    path('case', views.case, name='case'),
    path('reminders', views.reminders, name='reminders'),
]
