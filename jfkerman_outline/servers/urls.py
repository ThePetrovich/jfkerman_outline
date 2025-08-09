from django.urls import  path
from jfkerman_outline.servers.views import *

app_name = "servers"

urlpatterns = [
    path("servers/", OutlineServerListView.as_view(), name="server_list"),
    path("servers/<slug:server_slug>/keys/", OutlineServerKeyView.as_view(), name="server_keys"),
    path("servers/<slug:server_slug>/keys/create/", OutlineServerKeyCreateView.as_view(), name="server_key_create"),
    path("servers/<slug:server_slug>/keys/<int:pk>/update/", OutlineServerKeyUpdateView.as_view(), name="server_key_update"),
    path("servers/<slug:server_slug>/keys/<int:pk>/delete/", OutlineServerKeyDeleteView.as_view(), name="server_key_delete"),
    path("mykeys/", UserKeysView.as_view(), name="my_keys"),
    path("mykeys/<int:pk>/update/", OutlineServerKeyUpdateView.as_view(), name="mykeys_update"),
    path("mykeys/<int:pk>/delete/", OutlineServerKeyDeleteView.as_view(), name="mykeys_delete"),
    path("delete_all", OutlineServerDeleteAllKeysView.as_view(), name="delete_all_keys"),
    path("delete_all/<slug:server_slug>", OutlineServerDeleteAllKeysView.as_view(), name="delete_server_keys"),]