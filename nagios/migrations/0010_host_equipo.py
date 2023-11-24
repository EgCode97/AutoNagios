# Generated by Django 4.2.5 on 2023-11-24 20:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_equipo_ip'),
        ('nagios', '0009_alter_host_template'),
    ]

    operations = [
        migrations.AddField(
            model_name='host',
            name='equipo',
            field=models.ForeignKey(blank=True, db_column='NagHstEquID', null=True, on_delete=django.db.models.deletion.CASCADE, to='core.equipo'),
        ),
    ]