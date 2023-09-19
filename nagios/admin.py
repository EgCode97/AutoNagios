from django.contrib import admin
from .models import Host, HostGroup

@admin.register(Host)
class HostAdmin(admin.ModelAdmin):
    list_display = ('id', 'hostname', 'ip', 'alias')

@admin.register(HostGroup)
class HostGroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'alias')