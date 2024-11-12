from django.contrib import admin
from django.db import models
from django.forms import Textarea, TextInput
# from django_json_widget.widgets import JSONEditorWidget


class BabelBaseModelAdmin(admin.ModelAdmin):
    """Base Model Admin for all Admin Classes"""

    class Media:
        pass
        # TODO: Here we can style and js-ify the Django Admin by importing the custom css/js
        # js = ("js/admin/privatize_admin.js",)
        # css = {"all": ("css/admin/privatize_admin.css",)}

    save_on_top = True
    formfield_overrides = {
        models.CharField: {"widget": TextInput(attrs={"style": "width:100%;"})},
        # models.JSONField: {"widget": JSONEditorWidget(width="100%", height="250px")},
        models.TextField: {
            "widget": Textarea(attrs={"style": "width:100%; height:250px;"})
        },
    }
