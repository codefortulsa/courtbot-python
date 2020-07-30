from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('schedule_reminders', views.schedule_reminders, name='schedule_reminders'),
    path('unsubscribe_reminders', views.unsubscribe_reminders, name='unsubscribe_reminders'),
    path('send_verification_code', views.send_verification_code, name='send_verification_code')
]