from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ServersMarzbanConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "jfkerman_outline.servers_marzban"
    verbose_name = _("Servers Marzban")

    def ready(self):
        try:
            import jfkerman_outline.servers_marzban.signals  # noqa: F401
        except ImportError:
            pass

