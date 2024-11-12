import os
import re

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Count

from babelbase.models import Content


class Command(BaseCommand):
    """
    This management command iterates through all templates and get_or_creates the translations from the
    templates. This way, it's easy to update the translation state of an instance.

    RUN: python manage.py manage_content_i18n_translations
    """

    all_matches = {}
    found_matches = 0
    new_matches = 0

    pattern_any_thing = r'[\s\w"\']+'
    pattern_slug_param = r'\s+["\']([a-zA-Z0-9_-]+)["\']\s+'
    pattern_unicode = r'["\']([\p{L}]+)["\']'
    negative_lookahead_until_pattern = r"(?!{%)(.*?)"

    pattern_get_content = r"""
    {%\s*                           # Open brackets
    (get_content)\s+                # keyword
    ["\']([a-zA-Z0-9_-]+)["\']\s+   # first param   (namespace)
    ["\']([a-zA-Z0-9_-]+)["\']\s+   # second param  (key)
    ["\']([^"\']+)["\']             # third param  (free text)
    \s*%}
    """

    pattern_blockcontent_i18n = r"""
    {%\s*
    (blockcontent_i18n)\s+                      # keyword
    ["\']([a-zA-Z0-9_-]+)["\']\s+               # first param   (namespace)
    ["\']([a-zA-Z0-9_-]+)["\']\s*%}             # second param  (key)
    (.*?)(?={%\s*endblockcontent_i18n\s*%}|$)    # third param  (free text)
    """

    def get_template_path_list(self):
        template_paths = []
        directory_path = settings.TEMPLATES[0]["DIRS"][0]
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                if file.endswith(".html"):
                    template_paths.append(os.path.join(root, file))
        return template_paths

    def match_template_tags(self, content):
        # matches the get_content and bkockcontent_i18n tags
        matches = []
        matches_get_content = re.findall(
            self.pattern_get_content, content, re.DOTALL | re.VERBOSE
        )
        matches.extend(matches_get_content)
        matches_blockcontent_i18n = re.findall(
            self.pattern_blockcontent_i18n, content, re.DOTALL | re.VERBOSE
        )
        matches.extend(matches_blockcontent_i18n)
        return matches

    def get_or_create_content(self):
        # Fetches the content object and
        for path, match_list in self.all_matches.items():
            relative_template_path = path.split(
                "kinderwunschpraxis_stuttgart_villa_haag/templates/"
            )[1]
            # TODO: only if command is verbose
            # print(relative_template_path)
            for match in match_list:
                object, created = Content.objects.get_or_create(
                    view_identifier=match[1],
                    key_identifier=match[2],
                    defaults={"snippet_de": match[3]},
                )
                if object:
                    object.found_in(relative_template_path)
                    object.save()
                    self.found_matches += 1
                    self.new_matches += created

    def makedbtranslations(self):
        self.all_matches = {}
        for template_path in self.get_template_path_list():
            self.all_matches[template_path] = []
            with open(template_path) as file:
                self.all_matches[template_path].extend(
                    self.match_template_tags(file.read())
                )
        # Update the database
        self.get_or_create_content()
        # Print statistics
        print(f"Found {self.found_matches} translation in total.")
        print(f"Found {self.new_matches} new translations.")

    def finddbtranslations_duplicates(self):
        duplicates = (
            Content.objects.values("snippet_en")
            .annotate(text_count=Count("snippet_en"))
            .filter(text_count__gt=1)
        )
        if not duplicates:
            print("No duplicates found")
            return len(duplicates)
        for duplicate in duplicates:
            text_value = duplicate["snippet_en"]
            count = duplicate["text_count"]
            print(f"Text: {text_value}, Count: {count}")

    def finddbtranslations_stale(self):
        print("NOT IMPLEMENTED YET")

    def handle(self, *args, **options):
        print("===\nManage content_i18n translations:\n===")
        print("\nFind new translations in templates...")
        self.makedbtranslations()
        print("\nFind potential duplicate translations in the database...")
        self.finddbtranslations_duplicates()
        print(
            "\nFind potential stale translations in the database, but not in the template.."
        )
        self.finddbtranslations_stale()
