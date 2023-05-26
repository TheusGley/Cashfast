from django.apps import AppConfig


class BondConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bond'
    def ready(self) :
        from bond import scheduler
        scheduler.start()
    
        
