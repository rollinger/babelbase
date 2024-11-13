"""
BabelBase comes with two main template tags: babel and babelblock.

The babel tag is used to translate a single string, while the babelblock tag is used to translate a block of text.
"""

from django import template
from django.conf import settings
from django.conf.urls.i18n import is_language_prefix_patterns_used
from django.template import Library

from babelbase.models import TranslationSource

register = Library()


@register.simple_tag(takes_context=False)
def untranslate_url(path):
    """Returns the path without a language code prefix, if found"""
    path_parts = path.strip("/").split("/")
    if path_parts[0] in dict(settings.LANGUAGES):
        untranslated_path = "/" + "/".join(path_parts[1:])
    else:
        untranslated_path = "/" + "/".join(path_parts)
    return untranslated_path


@register.simple_tag(takes_context=False)
def translate_url(path, language_code):
    def reassemble_path(components):
        path = "/" + "/".join(components)
        return path

    # Get the untranslated url, default language and the prefixing status
    untranslated_path = untranslate_url(path)
    default_language = settings.LANGUAGE_CODE
    prefix_pattern_status = is_language_prefix_patterns_used(settings.ROOT_URLCONF)

    # Strip leading and trailing slashes and split the untranslated_path into it's component
    path_parts = untranslated_path.strip("/").split("/")

    # LocalePrefixPattern Consideration
    if not prefix_pattern_status[0]:
        # If i18n_patterns() is NOT used in the URLconf return the bare path
        return reassemble_path(path_parts)
    if not prefix_pattern_status[1] and language_code == default_language:
        # If the default language should NOT be prefixed
        return reassemble_path(path_parts)

    # Otherwise add prefix the language code and reassemble
    path_parts.insert(0, language_code)
    return reassemble_path(path_parts)


@register.simple_tag(takes_context=True)
def babel(context, namespace, identifier, placeholder=""):
    # Fetch Translation target from source
    translation_target = None
    translation_source = TranslationSource.objects.get_source_or_none(
        namespace, identifier
    )
    if translation_source:
        translation_target = translation_source.get_translation()
    # Output Fork
    if translation_target:
        return translation_target.content
    elif translation_source:
        return translation_source.content
    else:
        return placeholder


@register.tag
def babelblock(parser, token):
    return BabelBlockNode()


class BabelBlockNode(template.Node):
    def render(self, context):
        return ""
