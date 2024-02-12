from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ServersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "jfkerman_outline.servers"
    verbose_name = _("Servers")

    def ready(self):
        try:
            import jfkerman_outline.servers.signals  # noqa: F401
        except ImportError:
            pass

