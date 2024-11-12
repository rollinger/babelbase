"""
BabelBase comes with two main template tags: babel and babelblock.

The babel tag is used to translate a single string, while the babelblock tag is used to translate a block of text.
"""

from django import template
from django.template import Library

register = Library()


@register.simple_tag(takes_context=True)
def babel(context, namespace, identifier, placeholder=""):
    return placeholder


@register.tag
def babelblock(parser, token):
    return BabelBlockNode()


class BabelBlockNode(template.Node):
    def render(self, context):
        return ""
