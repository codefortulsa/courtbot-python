from django.db import models

from phonenumber_field.modelfields import PhoneNumberField


class Alert(models.Model):
    when = models.DateField()
    to = PhoneNumberField()
    what = models.CharField(max_length=255)
    sent = models.BooleanField(default=False)
