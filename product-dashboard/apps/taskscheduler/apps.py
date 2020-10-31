from django.apps import AppConfig


class TaskschedulerConfig(AppConfig):
    name = 'apps.taskscheduler'

    def ready(self):
        from apps.taskscheduler import management
        
        management.start()
