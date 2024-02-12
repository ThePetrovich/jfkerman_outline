from django.contrib import admin

from .models import OutlineServer, OutlineServerKey

admin.site.register(OutlineServer)
admin.site.register(OutlineServerKey)