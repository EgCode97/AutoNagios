from django.db import models

# from django.db.models.signals import post_save, pre_delete
# from django.dispatch import receiver

from decouple import config
import subprocess

NAGIOS_DIR = config('NAGIOS_DIR')

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
        verbose_name = 'Descripcion del host',
        max_length   = 100,
        db_column    = 'NagHstDsc',
    )

    # TODO hostgroup debe soportar multiples valores
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

    # TODO hostgroup debe soportar multiples valores
    hostgroup = models.ForeignKey(
        'nagios.HostGroup',
        verbose_name = 'Hostgroup', 
        on_delete    = models.SET_NULL,
        db_column    = 'NagHstGrpID',
        null=True, blank=True
    )

    def __str__(self):
        return self.hostname
    
    def create_nagios_cfg(self, write_parent:bool=True, write_hostgroup:bool=True):
        cfg_fields = {
            '# idtag'  : self.id,
            'address'  : self.ip,
            'host_name': self.hostname,
            'alias'    : self.alias,
            'use'      : self.template
        }

        if self.parents and write_parent:
            cfg_fields['parents'] = self.parents

        if self.hostgroup and write_hostgroup:
            cfg_fields['hostgroups'] = self.hostgroup
        
        cfg_content = 'define host {\n'
        for key, value in cfg_fields.items():
            cfg_content += f'{key}\t{value}\n'

        cfg_content += '}'
        
        with open(f'{NAGIOS_DIR + self.hostname}.cfg', 'w') as f:
            f.write(cfg_content)

        subprocess.run('systemctl restart nagios', shell=True)



class HostGroup(models.Model):
    nombre = models.CharField(
        verbose_name = 'Nombre',
        max_length   = 50,
        unique       = True,
        db_column    = 'NagHstGrpNom',
    )

    alias = models.CharField(
        verbose_name = 'Descripcion del grupo',
        max_length   = 100,
        db_column    = 'NagHstGrpDsc',
    )

    def __str__(self) -> str:
        return self.nombre

    def crear_nagios_cfg(self):
        cfg_dict = {'hostgroup_name':self.nombre, 'alias':self.alias}
        cfg_str = 'define hostgroup {\n'
        for key, value in cfg_dict.items():
            cfg_str += f'{key}\t{value}\n'
        cfg_str += '}'

        with open(f'{NAGIOS_DIR}{self.nombre}.cfg', 'w') as f:
            f.write(cfg_str)

        subprocess.run('systemctl restart nagios', shell=True)
