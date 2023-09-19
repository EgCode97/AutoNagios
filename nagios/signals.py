from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import Host, HostGroup, NAGIOS_DIR
import subprocess


# -----------------------------------------------------------------
# Signals de Host
# -----------------------------------------------------------------
@receiver(post_save, sender=Host)
def update_nagios_hosts(sender, instance:Host, created, **kwargs):
    instance.create_nagios_cfg()

@receiver(pre_delete, sender=Host)
def delete_nagios_hosts(sender, instance:Host, **kwargs):
    'Elimina el cfg de configuracion del host que ha sido eliminado y actualiza los hosts que lo tenian referenciado como padre'
    # Elimina el archivo de configuracion actual para el host en cuestion
    subprocess.run(f'rm {NAGIOS_DIR + instance.hostname}.cfg', shell=True)
    # Actualiza la configuracion de los hosts cuyo parent es el host que ha sido eliminado 
    # Es necesario indicar write_parent=False ya que por dispararse antes de eliminar el host de la db
    # aquellos hosts que lo referencien como padre aun no tendran el valor del FK en NULL
    [host.create_nagios_cfg(write_parent=False) for host in Host.objects.filter(parents=instance)]
    # reinicia nagios
    subprocess.run('systemctl restart nagios', shell=True)



# -----------------------------------------------------------------
# Signals de HostGroup
# -----------------------------------------------------------------
@receiver(post_save, sender=HostGroup)
def update_nagios_hostgroups(sender, instance:Host, created, **kwargs):
    instance.crear_nagios_cfg()

@receiver(pre_delete, sender=HostGroup)
def delete_nagios_hostgroups(sender, instance:Host, **kwargs):
    'Elimina el cfg de configuracion del hostgroup que ha sido eliminado y actualiza los hosts que pertencian al mismo'
    # Elimina el archivo de configuracion actual para el host en cuestion
    subprocess.run(f'rm {NAGIOS_DIR + instance.nombre}.cfg', shell=True)
    # Actualiza la configuracion de los hosts cuyo parent es el host que ha sido eliminado 
    # Es necesario indicar write_hostgroup=False ya que por dispararse antes de eliminar el hostgroup de la db
    # aquellos hosts que lo referencien aun no tendran el valor del FK en NULL
    [host.create_nagios_cfg(write_hostgroup=False) for host in Host.objects.filter(hostgroup=instance)]
    
    # reinicia nagios
    subprocess.run('systemctl restart nagios', shell=True)
