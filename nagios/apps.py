from django.apps import AppConfig


class NagiosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'nagios'

    def ready(self):
        import nagios.signals