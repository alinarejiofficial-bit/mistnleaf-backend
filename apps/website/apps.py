from django.apps import AppConfig


class WebsiteConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.website"
    label = "website"
    verbose_name = "Public Website"
