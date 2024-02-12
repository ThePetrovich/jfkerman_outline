from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views import defaults as default_views
from django.views.generic import TemplateView
from jfkerman_outline.servers.views import OutlineServerListView, OutlineServerKeyView, OutlineServerKeyCreateView, OutlineServerKeyUpdateView, OutlineServerKeyDeleteView

urlpatterns = [
    path("", TemplateView.as_view(template_name="pages/home.html"), name="home"),
    path("about/", TemplateView.as_view(template_name="pages/about.html"), name="about"),
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    # User management
    path("users/", include("jfkerman_outline.users.urls", namespace="users")),
    path("accounts/", include("allauth.urls")),
    # Your stuff: custom urls includes go here
    path("servers/", OutlineServerListView.as_view(), name="server_list"),
    path("servers/<slug:server_slug>/keys/", OutlineServerKeyView.as_view(), name="server_keys"),
    path("servers/<slug:server_slug>/keys/create/", OutlineServerKeyCreateView.as_view(), name="server_key_create"),
    path("servers/<slug:server_slug>/keys/<int:pk>/update/", OutlineServerKeyUpdateView.as_view(), name="server_key_update"),
    path("servers/<slug:server_slug>/keys/<int:pk>/delete/", OutlineServerKeyDeleteView.as_view(), name="server_key_delete"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
