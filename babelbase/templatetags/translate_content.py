import logging

# import sentry_sdk
from django import template
from django.conf import settings
from django.template import Library, Template, TemplateSyntaxError
from django.urls import reverse
from django.utils.html import escape
from django.utils.safestring import mark_safe

from babelbase.models import Content

register = Library()

TEMPLATE_TOKEN_REVERSAL_DICT = {
    "TEXT": "{}",
    "BLOCK": "{{% {} %}}",
    "VAR": "{{{{ {} }}}}",
    "COMMENT": "{{# {} #}}",
}

TEMPLATE_TOKEN_ESCAPE_DICT = {
    "{%": "{% templatetag openblock %}",
    "%}": "{% templatetag closeblock %}",
    "{{": "{% templatetag openvariable %}",
    "}}": "{% templatetag closevariable %}",
    "{": "{% templatetag openbrace %}",
    "}": "{% templatetag closebrace %}",
    "{#": "{% templatetag opencomment %}",
    "#}": "{% templatetag closecomment %}",
}

MISSING_TRANSLATION_HTML = """
<span style="color:red">MISSING TRANSLATION: {text}</span>
<span><small><a style="text-decoration: underline;"
href="{admin_add_url}?view_identifier={view_id}&key_identifier={key_id}&snippet_de={text}"
target="_blank">(CREATE)</a></small></span>
"""

ADMIN_CHANGE_TRANSLATION_HTML = """
<span><small><a style="text-decoration: underline;" href="{admin_change_url}"
target="_blank">(EDIT)</a></small></span>
"""


def user_can_edit_translations(request):
    if settings.ALLOW_DB_CONTENT_FRONTEND_EDIT:
        if hasattr(request, "user") and request.user.is_staff:
            return True
    return False


def escape_templatetags(placeholder):
    """Replaces all occurrences of django template tag with the templatetag X

    See: https://docs.djangoproject.com/en/4.2/ref/templates/builtins/#templatetag
    """

    for key, value in TEMPLATE_TOKEN_ESCAPE_DICT.items():
        placeholder = placeholder.replace(key, value)
    return placeholder


@register.simple_tag(takes_context=True)
def get_content(context, view_id, key_id, placeholder=""):
    """Returns the text for a specific view_id / key_id combination.

    1) tries to find the combination in the context, as provided by the TranslationSnippetMixin
    2) if not in context attempts to fetch the combination from the database
    3) if no TranslatableSnippet was found, and in DEBUG mode, returns a nice error message, with the option to
    create that TranslatableSnippet. If DEBUG is False: returns empty string.

    view_id: namespace in the database lookup
    key_id: identifier in the database lookup
    text: The text that should be used as the english version
    """
    translatable_text = None
    snippet_id = None
    if "view_identifier_list" in context and view_id in context["view_identifier_list"]:
        # return mark_saved text from the buffered Content from ContentMixin
        if (view_id, key_id) in context:
            translatable_text = context[(view_id, key_id)][1]
            snippet_id = context[(view_id, key_id)][0]
    else:
        # Attempt to fetch view/key combination inplace
        translatable_snippet = Content.objects.get_translatable_or_none(view_id, key_id)
        if translatable_snippet:
            translatable_text = translatable_snippet.snippet
            snippet_id = translatable_snippet.id

    # Return Rendered Text
    # Check if we have a text and not just whitespace
    if translatable_text and not translatable_text.isspace():
        # TODO: Consider vanilla python instead of Template() rendering for performance reasons
        translatable_text_template = Template(translatable_text)
        rendered_translatable_text = translatable_text_template.render(context)

        if user_can_edit_translations(context.request):
            if not snippet_id:  # Potentially never called
                snippet_id = Content.objects.get(
                    view_identifier=view_id, key_identifier=key_id
                ).id
            if settings.ALLOW_DB_CONTENT_FRONTEND_EDIT:
                # Add the edit link to the admin
                rendered_translatable_text += ADMIN_CHANGE_TRANSLATION_HTML.format(
                    admin_change_url=reverse(
                        "admin:content_i18n_content_change",
                        kwargs={"object_id": snippet_id},
                    ),
                )

        return mark_safe(rendered_translatable_text)

    else:
        # translatable text is not available: give out warning or log a warning in the background
        if user_can_edit_translations(context.request):
            # show key_id in case there is no placeholder
            if placeholder == "":
                placeholder = key_id

            return mark_safe(
                MISSING_TRANSLATION_HTML.format(
                    view_id=view_id,
                    key_id=key_id,
                    text=escape(placeholder),
                    admin_add_url=reverse("admin:content_i18n_content_add"),
                )
            )

        else:
            # If not text, and we are in production: empty string but log error in sentry
            log_message = (
                f"""Translatable Content is missing for {view_id}---{key_id}"""
            )
            # TODO: Re-enable Sentry Logging
            # if settings.PRODUCTION:
            #     # Only issue sentry in PRODUCTION MODE
            #     sentry_sdk.capture_message(log_message, level="warning")
            #
            # # otherwise, just log the message internally
            # else:
            #     logging.info(log_message)
            logging.info(log_message)
            # use placeholder (default: "") as standard output
            return mark_safe(placeholder)


def reverse_token(token):
    """Reverse the Token class into it's template pendant"""
    reversed_token = token.contents
    if token.token_type.name in TEMPLATE_TOKEN_REVERSAL_DICT.keys():
        reversed_token = TEMPLATE_TOKEN_REVERSAL_DICT[token.token_type.name].format(
            reversed_token
        )
    return reversed_token


#
# The get_content template tag in a block fashion
#
# TODO: refactor to get_blockcontent()
@register.tag
def blockcontent_i18n(parser, token):
    """Extracts the variables and calls the parser node"""
    try:
        tag_name, view_id, key_id = token.split_contents()
    except ValueError:
        raise TemplateSyntaxError(
            "%r takes two arguments: the view_id and key_id" % token.contents.split()[0]
        )
    # Reverse engineer the Tokens
    placeholder = ""
    while parser.tokens[-1].contents != "endblockcontent_i18n":
        placeholder += reverse_token(token=parser.tokens.pop())
    parser.delete_first_token()
    return BlockContentI18NNode(view_id, key_id, placeholder)


class BlockContentI18NNode(template.Node):
    """Fake block node returning the output of the get_content templatetag"""

    def __init__(self, view_id, key_id, placeholder):
        # Strip potential quotes from identifier
        self.view_id = view_id.strip("\"'")
        self.key_id = key_id.strip("\"'")
        self.placeholder = placeholder

    def render(self, context):
        # Does NOT render, just compiles and returns the get_content templatetag
        output = get_content(context, self.view_id, self.key_id, self.placeholder)
        return output
