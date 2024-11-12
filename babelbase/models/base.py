from django.db import models
from django.utils.translation import gettext_lazy as _


class TimestampMixin(models.Model):
    """
    Defines the timestamps for translation models
    """

    class Meta:
        abstract = True

    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)
