import subprocess
from pathlib import Path
from decouple import config
from django.db import models
from django.core.exceptions import ValidationError


MONITOREO_TRAFICO_DIR = Path(config('DIR_MONITOREO_TRAFICO')).resolve()

class Validadores:
    @staticmethod
    def valida_sin_espacios(texto:str):
        if ' ' in texto:
            raise ValidationError(
                ("El valor ingresado no debe contener espacios"),
                params={"texto": texto},
            )


class Ciudad(models.Model):
    nombre = models.CharField(
        max_length= 100,
        unique= True,
        db_column= 'CiuNom'
    )

    def __str__(self) -> str:
        return self.nombre
    

class Site(models.Model):
    nombre = models.CharField(
        max_length= 100,
        unique= True,
        db_column= 'SteNom'
    )

    ciudad = models.ForeignKey(
        to= Ciudad,
        default= 0,
        on_delete= models.SET_DEFAULT,
        db_column= 'SitCiuID'
    )

    def __str__(self) -> str:
        return self.nombre


class Equipo(models.Model):
    nombre = models.CharField(
        max_length=50,
        unique= True,
        validators=[
            Validadores.valida_sin_espacios
        ],
        db_column= 'EquNom'
    )

    descripcion = models.CharField(
        max_length= 100,
        db_column= 'EquDsc'
    )

    site = models.ForeignKey(
        to= Site,
        on_delete= models.SET_NULL,
        null= True, blank= True,
        db_column= 'EquSitID'
    )

    padres = models.ManyToManyField(
        to= 'core.Equipo',
        verbose_name= 'Padres',
        related_name= 'Equ_parents',
        blank= True
    )

    ip = models.GenericIPAddressField(
        verbose_name = 'IP',
        unique       = True,
        protocol     = 'IPv4',
        null= True, blank=True,
        db_column    = 'EquIP'
    )

    en_monitoreo = models.BooleanField(
        verbose_name= 'En monitoreo',
        default= False,
        db_column= 'EquMon'
    )

    monitorear_trafico = models.BooleanField(
        verbose_name= 'Monitoreando trafico',
        default= False,
        db_column= 'EquMonTra'
    )

    comunidad_snmp = models.CharField(
        verbose_name= 'Comunidad SNMP',
        max_length= 40,
        blank= True, null=True,
        db_column= 'EquComSNMP'
    )

    def __str__(self) -> str:
        return self.nombre
    
    def clean(self) -> None:
        self.apto_para_monitoreo()
        return super().clean()
        
    
    def apto_para_monitoreo(self):
        if not self.ip and self.en_monitoreo:
            raise ValidationError(
                ('Para ingresar el equipo a monitoreo debe indicar una direccion IPv4 valida'),
            )   
        
        if self.monitorear_trafico and not (self.comunidad_snmp and self.ip and self.en_monitoreo):
            raise ValidationError(
                ('Para monitorear el trafico debe indicar una direccion IPv4 valida, la comunidad SNMP y agregarlo al monitoreo'),
            )   
        
    def crear_cfg_monitoreo_trafico(self):
        Dir_cfg = MONITOREO_TRAFICO_DIR / str(self.site.ciudad.id) / str(self.site.id)
        Path.mkdir(Dir_cfg, parents=True, exist_ok=True)        

        with open(config('BASE_CONF_MONITOREO_TRAFICO'), 'r') as f:
            conf_base = f.read()

        conf_base = conf_base.replace('__IP__', self.ip)
        conf_base = conf_base.replace('__SNMPCOM__', self.comunidad_snmp)
        conf_base = conf_base.replace('__NOMBRE__', self.site.ciudad.nombre)
        conf_base = conf_base.replace('__EQUIPO__', str(self.id))

        with open(Dir_cfg / f'{str(self.id)}.conf', 'w') as conf:
            conf.write(conf_base)
            

    def eliminar_cfg_monitoreo_trafico(self) -> bool:
        "Evalua si existe el archivo de configuracion para monitorear el trafico del equipo. Si el archivo existe se elimina y el metodo devuelve True, en caso contrario devuelve False"
        archivo_conf = MONITOREO_TRAFICO_DIR / str(self.site.ciudad.id) / str(self.site.id) / f'{str(self.id)}.conf'
        if archivo_conf.exists():
            subprocess.run(f'rm {str(archivo_conf)}', shell=True)
            return True
        return False