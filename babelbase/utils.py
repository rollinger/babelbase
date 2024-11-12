from django.conf import settings
from django.utils.translation import get_language


def default_json_list():
    return []


def all_locales():
    return [lang[0] for lang in settings.LANGUAGES]


def translation_target_locales():
    return all_locales().remove(settings.LANGUAGE_CODE)


def get_current_locale(self):
    """Returns the name of current locale if available, otherwise returns the default language code."""
    lang = get_language()
    if not lang:
        lang = settings.LANGUAGE_CODE
    return lang
