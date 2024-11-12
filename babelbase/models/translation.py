from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from babelbase.babelbase.models.base import TimestampMixin
from babelbase.babelbase.utils import default_json_list, get_current_locale


class Namespace(models.Model):
    """Translation Namespace"""

    class Meta:
        verbose_name = _("Namespace")
        verbose_name_plural = _("Namespaces")
        ordering = ("-slug",)

    namespace = models.SlugField(
        _("Unique Namespace Slug"), max_length=255, allow_unicode=True, unique=True
    )

    def __str__(self):
        return self.namespace


class TranslationSource(TimestampMixin, models.Model):
    """Translation Source - See: LANGUAGE_CODE"""

    class Meta:
        verbose_name = _("Translation Source")
        verbose_name_plural = _("Translation Sources")
        ordering = ("-updated_at",)
        constraints = [
            models.UniqueConstraint(
                fields=["namespace", "identifier"],
                name="namespace-identifier-constraint",
            )
        ]

    namespace = models.ForeignKey(
        Namespace, related_name="translation_source_qs", on_delete=models.CASCADE
    )
    identifier = models.SlugField(
        _("Identifier Slug"), max_length=255, allow_unicode=True, unique=False
    )
    _lang = models.CharField(_("Language Code"), max_length=7)

    content = models.TextField(_("Content Source"), blank=True)

    changed = models.BooleanField(_("Has changed"), default=True)
    not_used = models.BooleanField(_("Not in use"), default=False)
    complete = models.BooleanField(_("Complete Translation"), default=False)

    template_registry = models.JSONField(
        _("Appearances in Templates"), default=default_json_list, blank=True
    )
    duplicates_registry = models.JSONField(
        _("Potential Duplicate Sources"), default=default_json_list, blank=True
    )

    def get_translation(self, locale=None):
        """Returns the source translation of the content if available, otherwise returns the source content"""
        if not locale:
            locale = get_current_locale()
        translation = self.translation_target_qs.filter(
            _lang=locale, approved=True
        ).first()
        if translation:
            return translation.content
        return self.content

    """
    def check_translation_completeness(self):
        # Checks if all possible translation targets have been approved
        for locale in translation_target_locales():
            if self.translation_target_qs.filter(_lang=locale)


    def translation_content_bitmask(self):
        bitmask = []
        for translation in self.translatables:
            if getattr(self, translation[1], None) != "":
                bitmask.append(translation[0])
        return bitmask

    def found_in(self, relative_path):
        if relative_path not in self.found_in_files:
            self.found_in_files.append(relative_path)
    """

    @property
    def lang(self):
        return self._lang

    def __str__(self):
        return f"{self.namespace}-{self.identifier}"

    def save(self, *args, **kwargs):
        if not self._lang:
            self._lang = settings.LANGUAGE_CODE
        return super().save(*args, **kwargs)


class TranslationTarget(TimestampMixin, models.Model):
    """Translation Target - See: LANGUAGES"""

    class Meta:
        verbose_name = _("Translation Target")
        verbose_name_plural = _("Translation Targets")
        ordering = ("-updated_at",)
        constraints = [
            models.UniqueConstraint(
                fields=["source", "_lang"],
                name="source-lang-constraint",
            )
        ]

    source = models.ForeignKey(
        TranslationSource,
        related_name="translation_target_qs",
        on_delete=models.CASCADE,
    )
    _lang = models.CharField(_("Language Code"), max_length=7)

    content = models.TextField(_("Content Translation"), blank=True)

    translated = models.BooleanField(_("Is translated"), default=False)
    approved = models.BooleanField(_("Translation approved"), default=False)

    @property
    def lang(self):
        return self._lang

    def save(self, *args, **kwargs):
        """Checks if translated and approved are set correctly"""
        if self.translated and not self.content:
            self.translated = False
        if self.approved and not self.translated:
            self.approved = False
        return super().save(*args, **kwargs)
