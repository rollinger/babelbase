from django.conf import settings
from django.views.generic.base import ContextMixin

from .models import Content


class ContentMixin(ContextMixin):
    """
    Inherits from Context Mixin and overrides the vanilla get_context_data to fetch translatables

    view_identifier: is a list of slug_strings that identifies the Translations to pull from the database
    """

    # NOTE: Make sure you intialize it with list brackets not just a string
    view_identifier_list = []

    def get_view_identifier_list(self):
        """Overriding actual attribute prepending the default identifier list from settings"""
        generic_view_identifier = settings.DB_TRANSLATION_DEFAULT_IDENTIFIER
        view_identifier = generic_view_identifier + self.view_identifier_list
        return view_identifier

    def fetch_translation_snippets_from_database(self):
        """Fetches the translations for the view_identifier from the database and takes the correct language version
        from the object"""
        translation_snippets = {}
        queryset = Content.objects.filter(
            view_identifier__in=list(self.get_view_identifier_list())
        )
        for record in queryset:
            # add view_id, key_id as lookup keys and the translated_text and object_id
            translation_snippets[(record.view_identifier, record.key_identifier)] = (
                record.id,
                record.snippet,
            )
        return translation_snippets

    def get_context_data(self, **kwargs):
        """
        Gets the context data and injects the Content found in the database. Also adds the
        view_identifier_list to the context for performance gain in the calling templatetag content.
        """
        kwargs = super().get_context_data(**kwargs)
        view_identifier_list = self.get_view_identifier_list()
        if view_identifier_list:
            self.translation_snippets = self.fetch_translation_snippets_from_database()
            kwargs.update(self.translation_snippets)
            kwargs.update({"view_identifier_list": view_identifier_list})
        return kwargs
