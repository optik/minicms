from django.forms import Textarea
from parler.forms import TranslatableModelForm
from django.conf import settings
from minicms.models import Page


class PageModelForm(TranslatableModelForm):
    class Meta:
        model = Page
        fields = '__all__'
        widgets = {
            'meta_keywords': Textarea(attrs={'rows': 2, 'cols': 100}),
            'meta_description': Textarea(attrs={'rows': 2}),
        }
        if hasattr(settings, 'CMS_WYSIWYG_EDITOR'):
            if settings.CMS_WYSIWYG_EDITOR == 'ckeditor':
                from ckeditor.widgets import CKEditorWidget
                widgets['content'] = CKEditorWidget()
            elif settings.CMS_WYSIWYG_EDITOR == 'tinymce':
                from tinymce.widgets import AdminTinyMCE
                widgets['content'] = AdminTinyMCE()
