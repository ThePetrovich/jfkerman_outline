from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.contrib import messages

from outline_vpn.outline_vpn import OutlineVPN

from .models import OutlineServer, OutlineServerKey


class OutlineServerListView(ListView):
    model = OutlineServer
    template_name = 'servers/outline_server_list.html'
    context_object_name = 'servers'


class OutlineServerKeyView(LoginRequiredMixin, ListView):
    model = OutlineServerKey
    template_name = 'servers/outline_server_keys.html'
    context_object_name = 'keys'

    def get_queryset(self):
        return OutlineServerKey.objects.filter(server__slug=self.kwargs['server_slug'], user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super(OutlineServerKeyView, self).get_context_data(**kwargs)
        context['server_slug'] = self.kwargs['server_slug']
        return context
        

class OutlineServerKeyCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = OutlineServerKey
    fields = ['name', 'data_limit']
    template_name = 'servers/outline_server_key_create.html'

    success_message = "Key created successfully"

    def get_context_data(self, **kwargs):
        context = super(OutlineServerKeyCreateView, self).get_context_data(**kwargs)
        context['server_slug'] = self.kwargs['server_slug']
        return context

    def get_success_url(self):
        if self.object == None:
            return reverse_lazy('server_list')
        else:
            return reverse_lazy('server_keys', kwargs={'server_slug': self.kwargs['server_slug']})

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.server = OutlineServer.objects.get(slug=self.kwargs['server_slug'])

        try:
            client = OutlineVPN(form.instance.server.api_url, form.instance.server.api_cert)

            new_key = client.create_key()
            client.rename_key(new_key.key_id, form.instance.user.username + '-' + form.instance.name)
    
            form.instance.key_id = new_key.key_id
            form.instance.key = new_key.access_url

            if form.instance.data_limit > 0:
                client.add_data_limit(new_key.key_id, form.instance.data_limit * 1024 * 1024) # Convert MB to bytes
            
        except Exception as e:
            messages.error(self.request, "Failed to create key: external API error", extra_tags='danger')
            return super().form_invalid(form)

        return super().form_valid(form)
        

class OutlineServerKeyUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = OutlineServerKey
    fields = ['name', 'data_limit']
    template_name = 'servers/outline_server_key_update.html'

    success_message = "Key updated successfully"

    def get_context_data(self, **kwargs):
        context = super(OutlineServerKeyUpdateView, self).get_context_data(**kwargs)
        context['server_slug'] = self.kwargs['server_slug']
        return context
    
    def get_success_url(self):
        if self.object == None:
            return reverse_lazy('server_list')
        else:
            return reverse_lazy('server_keys', kwargs={'server_slug': self.kwargs['server_slug']})

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.user != self.request.user:
            raise PermissionDenied
        return obj
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.server = OutlineServer.objects.get(slug=self.kwargs['server_slug'])

        try:
            client = OutlineVPN(form.instance.server.api_url, form.instance.server.api_cert)

            client.rename_key(form.instance.key_id, form.instance.user.username + '-' + form.instance.name)

            if form.instance.data_limit > 0:
                client.add_data_limit(form.instance.key_id, form.instance.data_limit * 1024 * 1024) # Convert MB to bytes
            else:
                client.delete_data_limit(form.instance.key_id)
            
        except Exception as e:
            messages.error(self.request, "Failed to update key: external API error", extra_tags='danger')
            return super().form_invalid(form)

        return super().form_valid(form)
    

class OutlineServerKeyDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = OutlineServerKey
    template_name = 'servers/outline_server_key_confirm_delete.html'
    context_object_name = 'key'

    success_message = "Key deleted successfully"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.user != self.request.user:
            raise PermissionDenied
        return obj

    def get_success_url(self):
        if self.object == None:
            return reverse_lazy('server_list')
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
            messages.error(self.request, "Failed to update key: external API error", extra_tags='danger')
            raise e

        messages.info(self.request, self.success_message, tags='danger')

        return super(OutlineServerKeyDeleteView, self).delete(request, *args, **kwargs)

