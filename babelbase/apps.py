from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class BabelBaseConfig(AppConfig):
    """App Config for the Babelbase Django App"""

    name = "babelbase"
    verbose_name = _("BabelBase Translations")
