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

from outline_vpn.outline_vpn import OutlineVPN

from .models import OutlineServer, OutlineServerKey


class OutlineServerListView(ListView):
    model = OutlineServer
    template_name = 'servers/outline_server_list.html'
    context_object_name = 'servers'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super(OutlineServerListView, self).get_context_data(**kwargs)
        for server in context['servers']:
            server.key_count = len(server.keys.filter(user=self.request.user))
        return context


class OutlineServerKeyView(LoginRequiredMixin, ListView):
    model = OutlineServerKey
    template_name = 'servers/outline_server_keys.html'
    context_object_name = 'keys'

    def get_queryset(self):
        return OutlineServerKey.objects.filter(server__slug=self.kwargs['server_slug'], user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super(OutlineServerKeyView, self).get_context_data(**kwargs)
        context['server_slug'] = self.kwargs['server_slug']
        context['server_name'] = OutlineServer.objects.get(slug=self.kwargs['server_slug']).name
        context['key_count'] = len(context['keys'])
        context['key_limit'] = OutlineServer.objects.get(slug=self.kwargs['server_slug']).keys_per_user
        return context
        

class OutlineServerKeyCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = OutlineServerKey
    fields = ['name', 'data_limit']
    template_name = 'servers/outline_server_key_create.html'

    success_message = _("Key created successfully")

    def get_context_data(self, **kwargs):
        context = super(OutlineServerKeyCreateView, self).get_context_data(**kwargs)
        context['server_slug'] = self.kwargs['server_slug']
        context['data_limit'] = OutlineServer.objects.get(slug=self.kwargs['server_slug']).max_data_per_key
        return context

    def get_success_url(self):
        if self.object == None:
            return reverse_lazy('server_list')
        else:
            return reverse_lazy('server_keys', kwargs={'server_slug': self.kwargs['server_slug']})

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.server = OutlineServer.objects.get(slug=self.kwargs['server_slug'])

        if len(form.instance.server.keys.filter(user=self.request.user)) >= form.instance.server.keys_per_user:
            messages.warning(self.request, _("Maximum keys per user reached, please delete other keys first"), extra_tags='warning')
            return super().form_invalid(form)

        try:
            client = OutlineVPN(form.instance.server.api_url, form.instance.server.api_cert)

            new_key = client.create_key()
            client.rename_key(new_key.key_id, form.instance.user.username + '-' + form.instance.name)
    
            form.instance.key_id = new_key.key_id
            form.instance.key = new_key.access_url

            if form.instance.data_limit > 0:
                if form.instance.server.max_data_per_key > 0 and form.instance.data_limit > form.instance.server.max_data_per_key:
                    messages.warning(self.request, _("Data limit exceeds server limit, setting to server limit"), extra_tags='warning')
                    form.instance.data_limit = form.instance.server.max_data_per_key
                client.add_data_limit(new_key.key_id, form.instance.data_limit * 1024 * 1024) # Convert MB to bytes
            else:
                if form.instance.server.max_data_per_key > 0:
                    messages.warning(self.request, _("Data limit exceeds server limit, setting to server limit"), extra_tags='warning')
                    client.add_data_limit(new_key.key_id, form.instance.server.max_data_per_key * 1024 * 1024)
                    form.instance.data_limit = form.instance.server.max_data_per_key
            
        except Exception as e:
            messages.error(self.request, _("Failed to create key: external API error"), extra_tags='danger')
            return super().form_invalid(form)

        return super().form_valid(form)
        

class OutlineServerKeyUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = OutlineServerKey
    fields = ['name', 'data_limit']
    template_name = 'servers/outline_server_key_update.html'

    context_object_name = 'key'

    success_message = _("Key updated successfully")

    def get_context_data(self, **kwargs):
        context = super(OutlineServerKeyUpdateView, self).get_context_data(**kwargs)
        context['server_slug'] = self.object.server.slug
        context['data_limit'] = self.object.server.max_data_per_key
        context['previous'] = self.request.META.get('HTTP_REFERER', reverse_lazy('my_keys'))
        return context
    
    def get_success_url(self):
        if self.object == None:
            return reverse_lazy('server_list')
        else:
            if 'server_slug' not in self.kwargs:
                return reverse_lazy('my_keys')
            else:
                return reverse_lazy('server_keys', kwargs={'server_slug': self.kwargs['server_slug']})

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.user != self.request.user:
            raise PermissionDenied
        return obj
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.server = self.object.server

        try:
            client = OutlineVPN(form.instance.server.api_url, form.instance.server.api_cert)

            client.rename_key(form.instance.key_id, form.instance.user.username + '-' + form.instance.name)

            if form.instance.data_limit > 0:
                if form.instance.server.max_data_per_key > 0 and form.instance.data_limit > form.instance.server.max_data_per_key:
                    messages.warning(self.request, _("Data limit exceeds server limit, setting to server limit"), extra_tags='danger')
                    form.instance.data_limit = form.instance.server.max_data_per_key
                client.add_data_limit(form.instance.key_id, form.instance.data_limit * 1024 * 1024) # Convert MB to bytes
            else:
                if form.instance.server.max_data_per_key > 0:
                    client.add_data_limit(form.instance.key_id, form.instance.server.max_data_per_key * 1024 * 1024)
                    form.instance.data_limit = form.instance.server.max_data_per_key
                    messages.warning(self.request, _("Data limit exceeds server limit, setting to server limit"), extra_tags='danger')
                else:
                    client.delete_data_limit(form.instance.key_id)
                    form.instance.data_limit = 0
            
        except Exception as e:
            messages.error(self.request, _("Failed to update key: external API error"), extra_tags='danger')
            return super().form_invalid(form)

        return super().form_valid(form)
    

class OutlineServerKeyDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = OutlineServerKey
    template_name = 'servers/outline_server_key_confirm_delete.html'
    context_object_name = 'key'

    success_message = _("Key deleted successfully")

    def get_context_data(self, **kwargs):
        context = super(OutlineServerKeyDeleteView, self).get_context_data(**kwargs)
        context['previous'] = self.request.META.get('HTTP_REFERER', reverse_lazy('my_keys'))
        return context

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.user != self.request.user:
            raise PermissionDenied
        return obj

    def get_success_url(self):
        if self.object == None:
            return reverse_lazy('server_list')
        else:
            if 'server_slug' not in self.kwargs:
                return reverse_lazy('my_keys')
            else:
                return reverse_lazy('server_keys', kwargs={'server_slug': self.kwargs['server_slug']})
        
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()

        try:
            client = OutlineVPN(self.object.server.api_url, self.object.server.api_cert)

            key = client.get_key(self.object.key_id) # Check if connection works

            try:

                client.delete_key(self.object.key_id)
            except Exception as e:
                pass
            
        except Exception as e:
            messages.error(self.request, _("Failed to delete key: external API error"), extra_tags='danger')
            raise e

        messages.info(self.request, self.success_message, tags='danger')

        return super(OutlineServerKeyDeleteView, self).delete(request, *args, **kwargs)
    

class OutlineServerDeleteAllKeysView(LoginRequiredMixin, ListView):
    model = OutlineServerKey
    template_name = 'servers/outline_server_key_confirm_delete_all.html'
    context_object_name = 'keys'

    def get_queryset(self):
        if 'server_slug' not in self.kwargs:
            return OutlineServerKey.objects.filter(user=self.request.user)
        else:
            return OutlineServerKey.objects.filter(user=self.request.user, server__slug=self.kwargs['server_slug'])
    
    def get_context_data(self, **kwargs):
        context = super(OutlineServerDeleteAllKeysView, self).get_context_data(**kwargs)
        context['key_count'] = len(context['keys'])
        context['previous'] = self.request.META.get('HTTP_REFERER', reverse_lazy('my_keys'))
        return context
    
    def post(self, request, *args, **kwargs):
        keys = self.get_queryset()

        for key in keys:
            client = OutlineVPN(key.server.api_url, key.server.api_cert)
            try:
                client.delete_key(key.key_id)
                key.delete()         
            except Exception as e:
                messages.error(self.request, _("Failed to delete key: external API error"), extra_tags='danger')
                raise e

        messages.info(self.request, _("All keys deleted successfully"))
        return HttpResponseRedirect(reverse_lazy('server_list'))
    

class OutlineServerDetailView(DetailView):
    model = OutlineServer
    template_name = 'servers/outline_server_detail.html'
    context_object_name = 'server'


class UserKeysView(LoginRequiredMixin, ListView):
    model = OutlineServerKey
    template_name = 'servers/user_keys.html'
    context_object_name = 'keys'
    paginate_by = 10

    def get_queryset(self):
        return OutlineServerKey.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super(UserKeysView, self).get_context_data(**kwargs)
        context['key_count'] = len(context['keys'])
        return context


