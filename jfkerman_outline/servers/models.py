from django.db import models
from jfkerman_outline.users.models import User
from django.utils.translation import gettext_lazy as _


class OutlineServer(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=100, db_index=True)

    country = models.CharField(max_length=100)

    url = models.CharField(max_length=255, default='', blank=True)
    port = models.IntegerField(default=0)
    
    api_url = models.CharField(max_length=255)
    api_cert = models.CharField(max_length=255)

    keys_per_user = models.IntegerField(default=0)
    max_data_per_key = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    

class OutlineServerKey(models.Model):
    server = models.ForeignKey(OutlineServer, on_delete=models.CASCADE, related_name='keys')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='keys')

    name = models.CharField(max_length=100, verbose_name=_('Key name'), help_text=_('Up to 100 characters long'))

    key_id = models.CharField(max_length=255, default='', blank=True, db_index=True)
    key = models.CharField(max_length=255, default='', blank=True)
    data_limit = models.BigIntegerField(default=0, verbose_name=_('Data limit (MB)'), help_text=_('Use 0 for unlimited data'))
    data_used = models.BigIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name