from django.apps import AppConfig

class MybinConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mybin'

#    def ready(self):
#        from mybin.utils import archiver
#        archiver.start()