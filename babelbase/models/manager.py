from django.db import models


class TranslationSourceManager(models.Manager):
    def get_source_or_none(self, namespace, identifier):
        """Tries to fetch the source directly and returns None if it does not exists in the database"""
        try:
            instance = self.get(namespace__namespace=namespace, identifier=identifier)
        except self.model.DoesNotExist:
            instance = None
        return instance


class ContentManager(models.Manager):
    def get_translatables(self, view_id, key_id=None):
        """Returns a queryset of translatable snippets
        1) Fetch the records lazily that matches with view_id / or the exact string
        2) Narrow down the records that match the key_id (list or exact)
        If view_id is not specified, return None
        """
        if not view_id:
            return None
        if type(view_id) is list:
            queryset = self.filter(view_identifier__in=view_id)
        elif type(view_id) is str:
            queryset = self.filter(view_identifier__iexact=view_id)
        if type(key_id) is list:
            queryset = queryset.filter(key_identifier__in=key_id)
        elif type(key_id) is str:
            queryset = queryset.filter(key_identifier__iexact=key_id)
        return queryset

    def get_translatable_or_none(self, view_id, key_id):
        """Tries to fetch an translateble item directly and returns None if not in the db"""
        try:
            instance = self.get(view_identifier=view_id, key_identifier=key_id)
        except self.model.DoesNotExist:
            instance = None
        return instance
