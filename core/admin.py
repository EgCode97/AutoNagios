from django.contrib import admin
from .models import Ciudad, Equipo, Site

@admin.register(Ciudad)
class CiudadAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')

@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'site', 'obten_ciudad', 'ip', 'en_monitoreo')
    list_filter = ('site', 'en_monitoreo')

    @admin.display(description='Ubicacion')
    def obten_ciudad(self, obj):
        try:
            return obj.site.ciudad.nombre
        except AttributeError:
            return str()

@admin.register(Site)
class AdminSite(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'ciudad')
