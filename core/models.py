from django.db import models
from django.core.exceptions import ValidationError

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