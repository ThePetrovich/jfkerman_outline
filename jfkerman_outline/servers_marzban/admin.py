from django.contrib import admin

from .models import MarzbanServer, MarzbanServerKey

admin.site.register(MarzbanServer)
admin.site.register(MarzbanServerKey)