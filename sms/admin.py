from django.contrib import admin

from .models import Lookup


class LookupAdmin(admin.ModelAdmin):
    pass


admin.site.register(Lookup, LookupAdmin)
