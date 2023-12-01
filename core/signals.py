from django.db.models.signals import pre_save, post_save, pre_delete, m2m_changed
from django.dispatch import receiver
from .models import Ciudad, Site, Equipo
import nagios.models as nagios_models
import subprocess



# -----------------------------------------------------------------
# Signals de Ciudad
# -----------------------------------------------------------------
@receiver(pre_save, sender=Ciudad)
def actualiza_ciudad_hostgroup(sender, instance:Ciudad, **kwargs):
    "Toma la ciudad modificada y actualiza el nombre del hostgroup de esta ciudad"
    try: 
        ciudad = Ciudad.objects.get(id = instance.id)
        hostgroup = nagios_models.HostGroup.objects.get(nombre= ciudad.nombre)
        # Elimina el archivo de configuracion actual para el hostgroup en cuestion si el mismo existe
        subprocess.run(f'rm {nagios_models.NAGIOS_DIR + hostgroup.nombre}.cfg', shell=True)
        hostgroup.nombre = instance.nombre
        hostgroup.alias = f"hosts {instance.nombre}"
        hostgroup.save()
    except (Ciudad.DoesNotExist, nagios_models.HostGroup.DoesNotExist):
        return
    
@receiver(post_save, sender=Ciudad)
def crea_ciudad_hostgroup(sender, instance:Ciudad, created, **kwargs):
    "Si se guardo una nueva ciudad crea un nuevo hostgroup para ella"
    if created:
        nagios_models.HostGroup(
            nombre= instance.nombre,
            alias= f"hosts {instance.nombre}"
        ).save()
    
@receiver(pre_delete, sender=Ciudad)
def elimina_ciudad_hostgroup(sender, instance:Ciudad, **kwargs):
    'Elimina el Hostgroup de nagios que hace referencia a la ciudad en cuestion'
    nagios_models.HostGroup.objects.get(nombre= instance.nombre).delete()
    subprocess.run('systemctl restart nagios', shell=True)



# -----------------------------------------------------------------
# Signals de Site
# -----------------------------------------------------------------
@receiver(pre_save, sender=Site)
def crea_site_hostgroup(sender, instance:Site, **kwargs):
    "Toma el site modificada y actualiza el nombre del hostgroup de este Site"
    try: 
        site = Site.objects.get(id = instance.id)
        hostgroup = nagios_models.HostGroup.objects.get(nombre= f'site_{site.nombre}')
        # Elimina el archivo de configuracion actual para el hostgroup en cuestion si el mismo existe
        subprocess.run(f'rm {nagios_models.NAGIOS_DIR + hostgroup.nombre}.cfg', shell=True)
        hostgroup.nombre = instance.nombre
        hostgroup.alias = f"hosts {instance.nombre}"
        hostgroup.save()
    except (Site.DoesNotExist, nagios_models.HostGroup.DoesNotExist):
        return
    
@receiver(post_save, sender=Site)
def actualiza_site_hostgroup(sender, instance:Site, created, **kwargs):
    "Toma la ciudad en modificada y actualiza el nombre del hostgroup de esta ciudad. Si es nueva, crea un nuevo hostgroup para la ciudad"
    if created:
        nagios_models.HostGroup(
            nombre= f'site_{instance.nombre}',
            alias= f'hosts site {instance.nombre}'
        ).save()

@receiver(pre_delete, sender=Site)
def elimina_site_hostgroup(sender, instance:Site, **kwargs):
    'Elimina el Hostgroup de nagios que hace referencia al site en cuestion'
    nagios_models.HostGroup.objects.get(nombre= instance.nombre).delete()
    subprocess.run('systemctl restart nagios', shell=True)

# -----------------------------------------------------------------
# Signals de Equipo
# -----------------------------------------------------------------
@receiver(post_save, sender=Equipo)
def actualiza_equipo(sender, instance:Equipo, **kwargs):
    "Toma el equipo modificado y si se marco como 'en monitoreo' cre un host de nagios"
    if instance.en_monitoreo:
        hostgroups = nagios_models.HostGroup.objects.filter(nombre__in=[f'site_{instance.site.nombre}', instance.site.ciudad.nombre])
        try:
            host = nagios_models.Host.objects.get(equipo__id=instance.id)
        except nagios_models.Host.DoesNotExist:
            host = nagios_models.Host.objects.create(
                ip= instance.ip,
                hostname= instance.nombre,
                alias= instance.descripcion,
                equipo= instance
            )

        host.hostgroups.set(hostgroups, clear=True)

        equipos_padres = instance.padres.all()
        hosts_padres = nagios_models.Host.objects.filter(equipo__in=equipos_padres)
        host.parents.set(hosts_padres)

        # Actualiza los parents de hosts cuyos equipos asociados tengan como padre un equipo
        # que se acaba de agregar al monitoreo
        equipos_hijos = Equipo.objects.filter(padres=instance, en_monitoreo=True)
        for equipo in equipos_hijos:
                nagios_models.Host.objects.get(equipo=equipo).parents.add(host)

        subprocess.run('systemctl restart nagios', shell=True)

    else:
        try:
            host = nagios_models.Host.objects.get(equipo__id= instance.id)
            host.delete()
        except nagios_models.Host.DoesNotExist:
            return
