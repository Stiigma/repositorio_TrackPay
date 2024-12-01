from django.apps import AppConfig


class PagosConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "pagos"


class UsuariosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'usuarios'

    def ready(self):
        from . import signals

        