from django.contrib import admin

from .models import Alert


class AlertAdmin(admin.ModelAdmin):
    pass


admin.site.register(Alert, AlertAdmin)
