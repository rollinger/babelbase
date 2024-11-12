from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from babelbase.admin.base import BabelBaseModelAdmin, BabelBaseStackedInline
from babelbase.models import Namespace, TranslationSource, TranslationTarget


@admin.register(Namespace)
class NamespaceModelAdmin(BabelBaseModelAdmin):
    """Namespace Model Admin"""

    list_display = ("namespace",)
    search_fields = ("namespace",)
    readonly_fields = ("id",)


class TranslationTargetStackedInline(BabelBaseStackedInline):
    """Translation Target as an inline"""

    model = TranslationTarget
    fk_name = "source"
    extra = 0
    readonly_fields = ("id", "source", "created_at", "updated_at")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    ("_lang", "translated", "approved"),
                    ("content",),
                    ("id", "created_at", "updated_at"),
                ),
            },
        ),
    )


@admin.register(TranslationSource)
class TranslationSourceAdmin(BabelBaseModelAdmin):
    """Translation Sources Model Admin"""

    list_display = (
        "namespace",
        "identifier",
        "content_preview",
        "changed",
        "not_used",
        "get_translation_bitmask",
        "complete",
    )
    search_fields = ("namespace", "identifier", "content")
    autocomplete_fields = ("namespace",)
    readonly_fields = ("id", "created_at", "updated_at")
    list_filter = ("changed", "not_used", "complete")
    list_display_links = ("content_preview",)
    list_editable = ("changed",)
    inlines = [
        TranslationTargetStackedInline,
    ]
    # actions = []
    fieldsets = (
        (
            _("General"),
            {
                "fields": (
                    ("namespace", "identifier", "_lang"),
                    ("changed", "not_used", "complete"),
                    ("content",),
                ),
            },
        ),
        (
            _("System Information"),
            {
                "classes": ("collapse",),
                "fields": (
                    ("id", "created_at", "updated_at"),
                    ("template_registry", "duplicates_registry"),
                ),
            },
        ),
    )

    @admin.display(
        description=_("Translations"),
    )
    def get_translation_bitmask(self, obj):
        """Returns a list of translated languages with their status"""
        return obj.translation_content_bitmask()
