import os

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import IntegrityError


class Command(BaseCommand):
    """
    This management command loads the fixture for the content_i18n translations.

    RUN: python manage.py load_content_i18n_fixture
    """

    help = "Update content_i18n fixtures"
    fixture_path = os.path.join(
        settings.ROOT_DIR,
        "kinderwunschpraxis_stuttgart_villa_haag/content_i18n/fixtures/content_i18n.json",
    )

    def handle(self, *args, **options):
        print("===\nLoad content_i18n translations:\n===")
        try:
            # See: https://docs.djangoproject.com/en/5.0/ref/django-admin/#loaddata
            call_command(
                "loaddata",
                "content_i18n.json",
                "--app=content_i18n",
                "--ignorenonexistent",
            )
        except IntegrityError as e:
            print(f"Operation could not be executed:\n{e}")
