from django.urls import path
from jfkerman_outline.servers_marzban.views import *

app_name = "servers_marzban"
urlpatterns = [
    path("", MarzbanServerListView.as_view(), name="home"),
    path("servers/", MarzbanServerListView.as_view(), name="server_list"),
    path("servers/<slug:server_slug>/keys/", MarzbanServerKeyView.as_view(), name="server_keys"),
    path("servers/<slug:server_slug>/keys/create/", MarzbanServerKeyCreateView.as_view(), name="server_key_create"),
    path("servers/<slug:server_slug>/keys/<int:pk>/update/", MarzbanServerKeyUpdateView.as_view(), name="server_key_update"),
    path("servers/<slug:server_slug>/keys/<int:pk>/delete/", MarzbanServerKeyDeleteView.as_view(), name="server_key_delete"),
    path("mykeys/", UserKeysView.as_view(), name="my_keys"),
    path("mykeys/<int:pk>/update/", MarzbanServerKeyUpdateView.as_view(), name="mykeys_update"),
    path("mykeys/<int:pk>/delete/", MarzbanServerKeyDeleteView.as_view(), name="mykeys_delete"),
    path("delete_all", MarzbanServerDeleteAllKeysView.as_view(), name="delete_all_keys"),
    path("delete_all/<slug:server_slug>", MarzbanServerDeleteAllKeysView.as_view(), name="delete_server_keys"),]