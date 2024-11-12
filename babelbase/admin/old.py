from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .base import BabelBaseModelAdmin
from babelbase.models import Content


@admin.register(Content)
class ContentAdmin(BabelBaseModelAdmin):
    list_display = (
        "view_identifier",
        "key_identifier",
        "get_content_preview",
        "incomplete_translation",
        "potential_duplicate",
        "potential_not_used",
        "get_translation_bitmask",
        "get_is_fully_translated",
        "updated_at",
        "created_at",
    )
    list_display_links = ("get_content_preview",)
    list_editable = ("incomplete_translation",)
    readonly_fields = [
        "id",
        "unique_id",
        "created_at",
        "updated_at",
        "view_identifier",
        "key_identifier",
    ]
    search_fields = ["content_en"]
    list_filter = (
        "view_identifier",
        "incomplete_translation",
        "potential_duplicate",
        "potential_not_used",
    )
    fieldsets = (
        (
            _("Snippet Identifiers"),
            {
                "fields": (
                    ("view_identifier", "key_identifier"),
                    (
                        "potential_duplicate",
                        "potential_not_used",
                        "incomplete_translation",
                    ),
                    ("snippet_de",),
                ),
            },
        ),
        (
            _("Translations"),
            {
                "classes": ("wide",),
                "fields": ("snippet_en",),
            },
        ),
        (
            _("System Information"),
            {
                "classes": ("collapse",),
                "fields": (
                    ("id", "unique_id"),
                    ("created_at", "updated_at"),
                    ("found_in_files"),
                ),
            },
        ),
    )

    @admin.display(
        boolean=True,
        description=_("Fully translated"),
    )
    def get_is_fully_translated(self, obj):
        """Returns true if the object is fully translated"""
        return obj.is_fully_translated

    @admin.display(
        description=_("Translations"),
    )
    def get_translation_bitmask(self, obj):
        """Returns a list of languages fields that are not empty"""
        return obj.translation_content_bitmask()

    @admin.display(
        description=_("Preview"),
    )
    def get_content_preview(self, obj, MAXC=45):
        """Return the first character of the english text"""
        return obj.snippet_de[:MAXC] + "..."
