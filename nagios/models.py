from django.db import models

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

import subprocess


# Create your models here.
class Host(models.Model):
    ip = models.GenericIPAddressField(
        verbose_name = 'IP',
        unique       = True,
        protocol     = 'IPv4',
        db_column    = 'NagHstIP'
    )

    hostname = models.CharField(
        verbose_name = 'Hostname',
        max_length   = 50,
        unique       = True,
        db_column    = 'NagHstNme',
    )

    alias = models.CharField(
        verbose_name = 'Hostname',
        max_length   = 100,
        db_column    = 'NagHstDsc',
    )

    parents = models.ForeignKey(
        'nagios.Host', 
        verbose_name = 'Padre', 
        on_delete    = models.SET_NULL,
        db_column    = 'NagHstParID',
        null=True, blank=True
    )

    template = models.CharField(
        verbose_name = 'Plantilla a utilizar',
        max_length   = 50,
        db_column    = 'NagHstTem',
    )

    def __str__(self):
        return self.hostname
    
    def create_nagios_cfg(self, write_parent:bool=True):
        print('ACTUALIZANDO CFG', self)
        cfg_fields = {
            '# idtag'  : self.id,
            'address'  : self.ip,
            'host_name': self.hostname,
            'alias'    : self.alias,
            'use'      : self.template
        }

        if self.parents and write_parent:
            cfg_fields['parents'] = self.parents
        
        cfg_content = 'define host {\n'

        for key, value in cfg_fields.items():
            cfg_content += f'{key}\t{value}\n'

        cfg_content += '}'
        
        with open(f'/usr/local/nagios/etc/objects/hosts/{self.hostname}.cfg', 'w') as f:
            f.write(cfg_content)

        subprocess.run('systemctl restart nagios', shell=True)


@receiver(post_save, sender=Host)
def update_nagios_hosts(sender, instance:Host, created, **kwargs):
    instance.create_nagios_cfg()

@receiver(pre_delete, sender=Host)
def delete_nagios_hosts(sender, instance:Host, **kwargs):
    subprocess.run(f'rm /usr/local/nagios/etc/objects/hosts/{instance.hostname}.cfg', shell=True)

    print(instance)

    [host.create_nagios_cfg(write_parent=False) for host in Host.objects.filter(parents=instance)]


    subprocess.run('systemctl restart nagios', shell=True)


Host(ip='192.168.0.1', hostname='router', alias='Wifi casa', template='linux-server').save()
Host(ip='192.168.0.101', hostname='elias-iPhone', alias='iPhone de Elias', template='linux-server', parents=Host.objects.get(ip='192.168.0.1')).save()