from typing import Any
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy
 
from marzpy import Marzban
from marzpy.api import user as marzban_user
import uuid, shortuuid
from asgiref.sync import async_to_sync

from .models import MarzbanServer, MarzbanServerKey


# monkey patch marzpy user

class NewMarzbanUser:
    def __init__(
        self,
        username: str,
        proxies: dict,
        inbounds: dict,  
        data_limit: float,
        data_limit_reset_strategy: str = "no_reset",
        status="",
        expire: float = 0,
        used_traffic=0,
        lifetime_used_traffic=0,
        created_at="",
        links=[],
        subscription_url="",
        excluded_inbounds={},
        note="",
        on_hold_timeout=0,
        on_hold_expire_duration=0,
        sub_updated_at=0,
        online_at=0,
        sub_last_user_agent: str = "",
        auto_delete_in_days: int = 0,
        **kwargs
    ):
        self.username = username
        self.proxies = proxies
        self.inbounds = inbounds
        self.expire = expire
        self.data_limit = data_limit
        self.data_limit_reset_strategy = data_limit_reset_strategy
        self.status = status
        self.used_traffic = used_traffic
        self.lifetime_used_traffic = lifetime_used_traffic
        self.created_at = created_at
        self.links = links
        self.subscription_url = subscription_url
        self.excluded_inbounds = excluded_inbounds
        self.note = note
        self.on_hold_timeout = on_hold_timeout
        self.on_hold_expire_duration = on_hold_expire_duration
        self.sub_last_user_agent = sub_last_user_agent
        self.online_at = online_at
        self.sub_updated_at = sub_updated_at
        self.auto_delete_in_days = auto_delete_in_days
        
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def __str__(self):
        """Returns a readable string representation of the User object"""
        attrs = [
            f"username='{self.username}'",
            f"status='{self.status}'",
            f"data_limit={self.data_limit}",
            f"expire={self.expire}",
            f"used_traffic={self.used_traffic}",
            f"lifetime_used_traffic={self.lifetime_used_traffic}",
            f"created_at='{self.created_at}'",
            f"subscription_url='{self.subscription_url}'",
            f"note='{self.note}'",
            f"on_hold_timeout={self.on_hold_timeout}",
            f"on_hold_expire_duration={self.on_hold_expire_duration}",
            f"sub_updated_at={self.sub_updated_at}",
            f"online_at={self.online_at}",
            f"auto_delete_in_days={self.auto_delete_in_days}"
        ]
        return f"User({', '.join(attrs)})"
    
    def __repr__(self):
        """Returns the same as __str__"""
        return self.__str__()
    
marzban_user.User = NewMarzbanUser
MarzbanUser = marzban_user.User


class MarzbanServerListView(ListView):
    model = MarzbanServer
    template_name = 'servers_marzban/marzban_server_list.html'
    context_object_name = 'servers'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super(MarzbanServerListView, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            for server in context['servers']:
                server.key_count = len(server.keys.filter(user=self.request.user))
        return context


class MarzbanServerKeyView(LoginRequiredMixin, ListView):
    model = MarzbanServerKey
    template_name = 'servers_marzban/marzban_server_keys.html'
    context_object_name = 'keys'

    def get_queryset(self):
        return MarzbanServerKey.objects.filter(server__slug=self.kwargs['server_slug'], user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super(MarzbanServerKeyView, self).get_context_data(**kwargs)
        context['server_slug'] = self.kwargs['server_slug']
        context['server_name'] = MarzbanServer.objects.get(slug=self.kwargs['server_slug']).name
        context['key_count'] = len(context['keys'])
        context['key_limit'] = MarzbanServer.objects.get(slug=self.kwargs['server_slug']).keys_per_user
        return context
        

class MarzbanServerKeyCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = MarzbanServerKey
    fields = ['name', 'data_limit']
    template_name = 'servers_marzban/marzban_server_key_create.html'

    success_message = gettext_lazy("Key created successfully")

    def get_context_data(self, **kwargs):
        context = super(MarzbanServerKeyCreateView, self).get_context_data(**kwargs)
        context['server_slug'] = self.kwargs['server_slug']
        context['data_limit'] = MarzbanServer.objects.get(slug=self.kwargs['server_slug']).max_data_per_key
        return context

    def get_success_url(self):
        if self.object == None:
            return reverse_lazy('marzban_servers:server_list')
        else:
            return reverse_lazy('marzban_servers:server_keys', kwargs={'server_slug': self.kwargs['server_slug']})

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.server = MarzbanServer.objects.get(slug=self.kwargs['server_slug'])

        if len(form.instance.server.keys.filter(user=self.request.user)) >= form.instance.server.keys_per_user:
            messages.warning(self.request, _("Maximum keys per user reached, please delete other keys first"), extra_tags='warning')
            return super().form_invalid(form)

        try:
            client = Marzban(form.instance.server.api_user, form.instance.server.api_password, form.instance.server.api_url)
            token = async_to_sync(client.get_token)()

            form.instance.key_id = uuid.uuid4()
            key_id_str = shortuuid.encode(form.instance.key_id)

            if form.instance.data_limit > 0:
                if form.instance.server.max_data_per_key > 0 and form.instance.data_limit > form.instance.server.max_data_per_key:
                    messages.warning(self.request, _("Data limit exceeds server limit, setting to server limit"), extra_tags='warning')
                    form.instance.data_limit = form.instance.server.max_data_per_key
            else:
                if form.instance.server.max_data_per_key > 0:
                    messages.warning(self.request, _("Data limit exceeds server limit, setting to server limit"), extra_tags='warning')
                    form.instance.data_limit = form.instance.server.max_data_per_key

            new_server_user = MarzbanUser(
                username=key_id_str,
                note=form.instance.user.username + '-' + form.instance.name,
                data_limit=form.instance.data_limit * 1024 * 1024,  # Convert MB to bytes
                inbounds={"vless": [form.instance.server.vless_inbound]},
                data_limit_reset_strategy="month",
                proxies={"vless": {}},
                expire=0,
                status="active" 
            )
            
            result = async_to_sync(client.add_user)(user=new_server_user, token=token)
            form.instance.config_id = result.username
            form.instance.config = result.links[0]
            
        except Exception as e:
            messages.error(self.request, _("Failed to create key: external API error"), extra_tags='danger')
            return super().form_invalid(form)

        return super().form_valid(form)
        

class MarzbanServerKeyUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = MarzbanServerKey
    fields = ['name', 'data_limit']
    template_name = 'servers_marzban/marzban_server_key_update.html'

    context_object_name = 'key'

    success_message = gettext_lazy("Key updated successfully")

    def get_context_data(self, **kwargs):
        context = super(MarzbanServerKeyUpdateView, self).get_context_data(**kwargs)
        context['server_slug'] = self.object.server.slug
        context['data_limit'] = self.object.server.max_data_per_key
        context['previous'] = self.request.META.get('HTTP_REFERER', reverse_lazy('marzban_servers:my_keys'))
        return context
    
    def get_success_url(self):
        if self.object == None:
            return reverse_lazy('marzban_servers:server_list')
        else:
            if 'server_slug' not in self.kwargs:
                return reverse_lazy('marzban_servers:my_keys')
            else:
                return reverse_lazy('marzban_servers:server_keys', kwargs={'server_slug': self.kwargs['server_slug']})

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.user != self.request.user:
            raise PermissionDenied
        return obj
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.server = self.object.server

        try:
            client = Marzban(form.instance.server.api_user, form.instance.server.api_password, form.instance.server.api_url)
            token = async_to_sync(client.get_token)()

            if form.instance.data_limit > 0:
                if form.instance.server.max_data_per_key > 0 and form.instance.data_limit > form.instance.server.max_data_per_key:
                    messages.warning(self.request, _("Data limit exceeds server limit, setting to server limit"), extra_tags='danger')
                    form.instance.data_limit = form.instance.server.max_data_per_key
            else:
                if form.instance.server.max_data_per_key > 0:
                    form.instance.data_limit = form.instance.server.max_data_per_key
                    messages.warning(self.request, _("Data limit exceeds server limit, setting to server limit"), extra_tags='danger')
                else:
                    form.instance.data_limit = 0

            new_server_user = MarzbanUser(
                username=form.instance.config_id,
                note=form.instance.user.username + '-' + form.instance.name,
                data_limit=form.instance.data_limit * 1024 * 1024,  # Convert MB to bytes
                inbounds={"vless": [form.instance.server.vless_inbound]},
                data_limit_reset_strategy="month",
                proxies={"vless": {}},
                expire=0,
                status="active" 
            )

            result = async_to_sync(client.modify_user)(form.instance.config_id, user=new_server_user, token=token)
            form.instance.config_id = result.username
            form.instance.config = result.links[0]
            
        except Exception as e:
            messages.error(self.request, _("Failed to update key: external API error"), extra_tags='danger')
            return super().form_invalid(form)

        return super().form_valid(form)
    

class MarzbanServerKeyDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = MarzbanServerKey
    template_name = 'servers_marzban/marzban_server_key_confirm_delete.html'
    context_object_name = 'key'

    success_message = gettext_lazy("Key deleted successfully")

    def get_context_data(self, **kwargs):
        context = super(MarzbanServerKeyDeleteView, self).get_context_data(**kwargs)
        context['previous'] = self.request.META.get('HTTP_REFERER', reverse_lazy('marzban_servers:my_keys'))
        return context

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.user != self.request.user:
            raise PermissionDenied
        return obj

    def get_success_url(self):
        if self.object == None:
            return reverse_lazy('marzban_servers:server_list')
        else:
            if 'server_slug' not in self.kwargs:
                return reverse_lazy('marzban_servers:my_keys')
            else:
                return reverse_lazy('marzban_servers:server_keys', kwargs={'server_slug': self.kwargs['server_slug']})
        
    def form_valid(self, form):
        try:
            client = Marzban(self.object.server.api_user, self.object.server.api_password, self.object.server.api_url)
            token = async_to_sync(client.get_token)()

            try:
                result = async_to_sync(client.delete_user)(self.object.config_id, token=token)
                if result != "success":
                    messages.error(self.request, _("Failed to delete key: external API error"), extra_tags='danger')
                    raise Exception("Failed to delete key from external API")
            except Exception as e:
                messages.error(self.request, _("Failed to delete key: external API error"), extra_tags='danger')
                raise e
            
        except Exception as e:
            messages.error(self.request, _("Failed to delete key: external API error"), extra_tags='danger')
            raise e

        return super().form_valid(form)
    

class MarzbanServerDeleteAllKeysView(LoginRequiredMixin, ListView):
    model = MarzbanServerKey
    template_name = 'servers_marzban/marzban_server_key_confirm_delete_all.html'
    context_object_name = 'keys'

    def get_queryset(self):
        if 'server_slug' not in self.kwargs:
            return MarzbanServerKey.objects.filter(user=self.request.user)
        else:
            return MarzbanServerKey.objects.filter(user=self.request.user, server__slug=self.kwargs['server_slug'])
    
    def get_context_data(self, **kwargs):
        context = super(MarzbanServerDeleteAllKeysView, self).get_context_data(**kwargs)
        context['key_count'] = len(context['keys'])
        context['previous'] = self.request.META.get('HTTP_REFERER', reverse_lazy('marzban_servers:my_keys'))
        return context
    
    def post(self, request, *args, **kwargs):
        keys = self.get_queryset()

        for key in keys:
            client = Marzban(key.server.api_user, key.server.api_password, key.server.api_url)
            token = async_to_sync(client.get_token)()

            try:
                async_to_sync(client.delete_user)(key.config_id, token=token)
                key.delete()         
            except Exception as e:
                messages.error(self.request, _("Failed to delete key: external API error"), extra_tags='danger')
                raise e

        messages.info(self.request, _("All keys deleted successfully"))
        return HttpResponseRedirect(reverse_lazy('marzban_servers:server_list'))
    

class MarzbanServerDetailView(DetailView):
    model = MarzbanServer
    template_name = 'servers_marzban/marzban_server_detail.html'
    context_object_name = 'server'


class UserKeysView(LoginRequiredMixin, ListView):
    model = MarzbanServerKey
    template_name = 'servers_marzban/user_keys.html'
    context_object_name = 'keys'
    paginate_by = 10

    def get_queryset(self):
        return MarzbanServerKey.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super(UserKeysView, self).get_context_data(**kwargs)
        context['key_count'] = len(context['keys'])
        return context


