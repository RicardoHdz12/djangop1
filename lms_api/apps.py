from django.apps import AppConfig

class LMSApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = "lms_api"

    def ready(self):
        import lms_api.signals