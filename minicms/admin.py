from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from parler.admin import TranslatableAdmin
from .models import *
from .forms import *


class BlockAdmin(TranslatableAdmin):
    list_display = ('code', 'modified', 'modified_by')
    fieldsets = (
        (None, {
            'fields': ('code', 'content'),
        }),
        ('Optional', {
            'fields': ('heading', 'link_to'),
        }),
    )


class VariableAdmin(admin.ModelAdmin):
    list_display = ('code', 'value')
    fieldsets = (
        (None, {
            'fields': ('code', 'value'),
        }),
    )


class PageAdmin(TranslatableAdmin):
    form = PageModelForm
    list_display = ('title', 'slug', 'code', 'parent', 'modified', 'modified_by')
    fieldsets = (
        (None, {
            'fields': ('code', 'is_homepage', 'parent', 'title', 'slug',),
        }),
        (_('Content'), {
            'fields': ('template', 'content',),
        }),
        (_('Metadata'), {
            'classes': ('collapse',),
            'fields': ('meta_title', 'meta_keywords', 'meta_description'),
        }),
    )

    def get_prepopulated_fields(self, request, obj=None):
        # can't use `prepopulated_fields = ..` because it breaks the admin validation
        # for translated fields. This is the official django-parler workaround.
        return {
            'slug': ('title',)
        }


admin.site.register(Block, BlockAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(Variable, VariableAdmin)
