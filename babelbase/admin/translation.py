from django.contrib import admin

from babelbase.babelbase.admin.base import BabelBaseModelAdmin
from babelbase.babelbase.models import Namespace, TranslationSource, TranslationTarget


@admin.register(Namespace)
class NamespaceModelAdmin(BabelBaseModelAdmin):
    """"""

    pass


@admin.register(TranslationSource)
class TranslationSourceAdmin(BabelBaseModelAdmin):
    """"""

    pass


@admin.register(TranslationTarget)
class TranslationTargetModelAdmin(BabelBaseModelAdmin):
    """"""

    pass
