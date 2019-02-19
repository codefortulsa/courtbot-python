from django.db import models

from phonenumber_field.modelfields import PhoneNumberField


class Lookup(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    from_phone = PhoneNumberField()
    what = models.CharField(max_length=255)
    done = models.BooleanField(default=False)
