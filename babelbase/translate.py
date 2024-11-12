import logging
import re

from django.conf import settings
from django.db.utils import ProgrammingError
from django.utils.functional import lazy

from babelbase.models import TranslationSource


def convert_curly_braces(text):
    """Streamlines double-curly braces syntax into a proper f-string interpolation format"""
    pattern = r"{{\s*([\w\d]+)\s*}}"

    def replace_match(match):
        return "{" + match.group(1) + "}"

    return re.sub(pattern, replace_match, text)


def context_interpolation(text, context):
    """Returns the text with the {{var}} replaced if in the context"""
    text = convert_curly_braces(text)
    interpolated_text = text.format(**context)
    return interpolated_text


class DatabaseTranslationBuffer:
    """
    Handles databased translation with view_id, key_id from within python code.

    Initializing the class, the translation_snippets are pre-loaded. When the gettext_db is called it will lookup the
    pre-loaded dictionary first before attempting another call to the db.

    Initialization:
    translation_namespace = ["user_tracks", "investor_qualification"]
    db_trans = DatabaseTranslationManager(translation_namespace)

    DB Buffered Retrieval:
    db_trans.gettext_lazy("view_id", "key_id", context={})
    """

    translation_content = {}

    def __init__(self, view_identifier_list=[]):
        """Namespace chaining and pr-loading"""
        generic_view_identifier = settings.DB_TRANSLATION_DEFAULT_IDENTIFIER
        self.view_identifier_list = generic_view_identifier + view_identifier_list
        # Pre-Loading
        self.prefetch_translations_from_db()

    def prefetch_translations_from_db(self):
        """
        Fetches the translations for the view_identifiers from the database.
        We require a try/except clause as this function is evaluated *before* django models are
        ready or migrated.
        """

        try:
            queryset = TranslationSource.objects.filter(
                view_identifier__in=list(self.view_identifier_list)
            )
            for record in queryset:
                # add view_id, key_id as lookup keys and the translatable object
                self.translation_content[
                    (record.view_identifier, record.key_identifier)
                ] = record

        # this clause prevents unittests to fail due to missing models at startup
        except ProgrammingError as error:
            # make sure it's a missing relation
            if "relation" in str(error):
                logging.error(
                    "TranslationSource model not available: please run migrations first"
                )
                return None

            # otherwise, raise error
            raise error

        return len(queryset)

    def get_object(self, view_id, key_id):
        """Returns the object which is not decided on a translation yet"""
        if (view_id, key_id) in self.translation_content:
            translatable_content = self.translation_content[(view_id, key_id)]
        else:
            translatable_content = TranslationSource.objects.get_translatable_or_none(
                view_id, key_id
            )
        if translatable_content:
            return translatable_content
        return None


def get_text_from_db_translation_buffer(
    buffer, view_id, key_id, context={}, placeholder=""
):
    """
    Handler for the lazily evaluated proxy db_gettext_lazy
    """
    if type(buffer) is DatabaseTranslationBuffer:
        translatable_content = getattr(buffer, "get_object")(view_id, key_id)
        if translatable_content:
            translatable_text = translatable_content.snippet
            translatable_text = context_interpolation(translatable_text, context)
            return translatable_text
    return f"MISSING {view_id}---{key_id}: {placeholder}"


db_gettext_lazy = lazy(get_text_from_db_translation_buffer, str)
