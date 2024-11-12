import os

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import IntegrityError


class Command(BaseCommand):
    """
    This management command updates the fixture for the content_i18n translations.

    RUN: python manage.py update_content_i18n_fixture
    """

    help = "Update content_i18n fixtures"
    fixture_path = os.path.join(
        settings.ROOT_DIR,
        "kinderwunschpraxis_stuttgart_villa_haag/content_i18n/fixtures/content_i18n.json",
    )

    def handle(self, *args, **options):
        print("===\nUpdate content_i18n translations:\n===")
        try:
            # See: https://docs.djangoproject.com/en/5.0/ref/django-admin/#dumpdata
            call_command(
                "dumpdata",
                "content_i18n",
                f"--output={self.fixture_path}",
                "--indent=4",
                "--natural-foreign",
            )
        except IntegrityError as e:
            print(f"Operation could not be executed:\n{e}")
