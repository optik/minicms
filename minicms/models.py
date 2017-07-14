# noqa E501
from lxml import html
import re
from django.db import models
from django.template.loader import get_template
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import get_language, ugettext_lazy as _
from django.conf import settings
from model_utils.models import TimeStampedModel
from ordered_model.models import OrderedModel
from parler.models import (TranslatableModel, TranslatedFields,
                           TranslatedFieldsModel, TranslatableManager)
from parler.fields import TranslatedField


user_model = settings.AUTH_USER_MODEL
# XXX: better use `from django.contrib.auth import get_user_model`?


class PageInfo:
    PROPERTIES = ('id', 'is_homepage', 'code', 'parent_id')
    TRANSLATED_PROPERTIES = ('slug', 'title', 'path')

    def __init__(self, **kwargs):
        for key in self.PROPERTIES:
            setattr(self, key, kwargs.get(key))
        self.set_translated(**kwargs)

        # self.path = self.slug  # TODO: missing complex path support, this needs to be generated

    def set_translated(self, **kwargs):
        language_code = kwargs.get('translations__language_code')
        for key in self.TRANSLATED_PROPERTIES:
            setattr(self, "%s__%s" % (key, language_code), kwargs.get("translations__" + key))

    def __getattr__(self, name):
        language = get_language()
        if not language or name not in self.TRANSLATED_PROPERTIES:
            raise AttributeError('Cannot determine language or attribute %s invalid' % name)
        return getattr(self, ('%s__%s' % (name, language)), None)

    def __repr__(self):
        props = self.PROPERTIES
        return "\n".join(["{0}: {1}".format(k, getattr(self, k)) for k in props])


class PageManager(TranslatableManager):
    _registry = None

    def __str__(self):
        return str(dir(self))

    def get_by_natural_key(self, pk_or_code):
        return self.get(pk_or_code)

    def reload_registry(self):
        if self.model is not None:
            snapshot = self.all().values(
                'id', 'is_homepage', 'code', 'parent_id',
                'translations__language_code', 'translations__slug', 'translations__title',
            )
            self._registry = []
            for row in snapshot:
                if len(self._registry) and self._registry[-1].id == row['id']:
                    self._registry[-1].set_translated(**row)
                    continue
                self._registry.append(PageInfo(**row))
        else:
            raise Exception('Cannot create page index')
        return self._registry

    @property
    def registry(self):
        return self._registry if self._registry is not None else self.reload_registry()

    def get_info(self, *args, **kwargs):
        assert not len(args) > 1, \
            "get_info can be called with up to one positional argument (int or str)"

        registry = self.registry  # forces registry creation

        if len(args):
            # attempt to detect the key
            pk_or_code = args[0]
            if isinstance(pk_or_code, int):  # PK
                return self.get_info(id=pk_or_code)
            elif isinstance(pk_or_code, str):  # code
                return self.get_info(code=pk_or_code)

        key, value = kwargs.popitem()
        if key not in PageInfo.TRANSLATED_PROPERTIES and key not in PageInfo.PROPERTIES:
            raise KeyError('"%s" is not a valid property, cannot search index' % key)
        info = registry and next((p for p in registry if getattr(p, key) == value), None)
        if not info:
            raise Page.DoesNotExist('Page info not found in index (searching by %s for "%s")' % (key, value))
        return info

    def get(self, *args, **kwargs):
        info = self.get_info(*args, **kwargs)
        return super(PageManager, self).get(id=info.id)

    def get_url(self, *args, **kwargs):
        from django.shortcuts import resolve_url
        silent = kwargs.pop('silent', '#404')
        try:
            info = self.get_info(**kwargs)
        except ObjectDoesNotExist as e:
            if silent:
                return silent if silent is True else silent
            else:
                raise e

        return resolve_url('minicms:page', path=info.path)


class Page(TimeStampedModel, TranslatableModel, OrderedModel):
    objects = PageManager()

    code_help = _("Assign a code to the page to be able to retrieve or \
                  link to it independently of the current language, \
                  slug or position in the page hierarchy")

    is_homepage = models.BooleanField(default=False, verbose_name=_('Is homepage?'))
    code = models.CharField(max_length=64,
                            null=True,
                            blank=True,
                            db_index=True,
                            verbose_name=_('Code'),
                            help_text=code_help)
    parent = models.ForeignKey("self",
                               null=True,
                               blank=True,
                               related_name="child_pages",
                               verbose_name=_('Parent page'))
    template = models.CharField(max_length=255,
                                null=True,
                                blank=True,
                                choices=getattr(settings, 'CMS_TEMPLATES', None),
                                verbose_name=_('Template'))
    created_by = models.ForeignKey(user_model, null=True,
                                   related_name='pages_created',
                                   on_delete=models.SET_NULL,
                                   verbose_name=_('Created by'))
    modified_by = models.ForeignKey(user_model, null=True,
                                    related_name='pages_modified',
                                    on_delete=models.SET_NULL,
                                    verbose_name=_('Modified by'))

    title = TranslatedField()
    slug = TranslatedField()
    content = TranslatedField()
    meta_title = TranslatedField()
    meta_keywords = TranslatedField()
    meta_description = TranslatedField()

    order_with_respect_to = 'parent'

    class Meta(OrderedModel.Meta):
        verbose_name = _("Page")
        verbose_name_plural = _("Pages")

    @property
    def path(self):
        return Page.objects.get_info(id=self.id).path

    def get_template_section_keys(self):
        from minicms.templatetags.minicms import ContentSectionNode
        template = get_template(self.template)
        nodes = template.template.nodelist.get_nodes_by_type(ContentSectionNode)
        return [n.name for n in nodes]

    def get_content_section(self, name):
        translation = self.get_translation(self.get_current_language())
        return translation.get_content_section(name)

    def __str__(self):
        try:
            title = self.title
        except Exception as e:
            title = '[untranslated]'
        key = self.code or self.pk
        return "%s (%s)" % (title, key,)

    def natural_key(self):
        return (self.code,) if self.code else (self.id,)

    def meta_keywords_as_array(self):
        return [item.strip() for item in self.meta_keywords.split(",")]


class PageTranslationManager(models.Manager):
    def get_by_natural_key(self, master, language_code):
        master_info = Page.objects.get_info(master)
        return self.get(master=master_info.id, language_code=language_code)


class PageTranslation(TranslatedFieldsModel):
    master = models.ForeignKey(Page, related_name='translations', null=True, on_delete=models.CASCADE)
    title = models.CharField(_('Title'), max_length=120)
    slug = models.SlugField(_('Slug'), unique=True, blank=True)
    content = models.TextField(_('Content'), blank=True)
    meta_title = models.CharField(_('Meta title'), blank=True, default="", max_length=255)
    meta_keywords = models.TextField(_('Meta keywords'), blank=True, default="", max_length=255)
    meta_description = models.TextField(_('Meta description'), blank=True, default="", max_length=255)

    objects = PageTranslationManager()
    _content_sections = None

    class Meta:
        db_table = 'minicms_page_translation'
        unique_together = ('language_code', 'master')
        verbose_name = _("Page translaton")

    @property
    def html_tree(self):
        if not hasattr(self, '_html_tree'):
            self._html_tree = html.fragment_fromstring(self.content, create_parent='body')
        return self._html_tree

    def natural_key(self):
        return self.master.natural_key() + (self.language_code,)
    natural_key.dependencies = ['minicms.page']

    def get_content_section(self, name):
        if self._content_sections is None:
            self._content_sections = {}
            sections = re.split(r'\s*<section data-section-id="(?P<id>.+)">', self.content)
            for id, content in zip(sections[1::2], sections[2::2]):
                self._content_sections[id] = re.sub(r'<\/section>\s*$', '', content)

        return self._content_sections.get(name, None)


class BlockManager(TranslatableManager):
    def get_by_natural_key(self, code):
        return self.get(code=code)


class Block(TimeStampedModel, TranslatableModel):
    code = models.CharField(max_length=64, unique=True, verbose_name=_('Code'))
    css_class = models.CharField(blank=True, null=True, max_length=64, verbose_name=_('CSS class'))
    created_by = models.ForeignKey(user_model, null=True,
                                   related_name='blocks_created',
                                   on_delete=models.SET_NULL,
                                   verbose_name=_('Created by')),
    modified_by = models.ForeignKey(user_model, null=True,
                                    related_name='blocks_modified',
                                    on_delete=models.SET_NULL,
                                    verbose_name=_('Modified by'))
    translations = TranslatedFields(
        heading=models.CharField(blank=True, null=True, max_length=250, verbose_name=_('Optional heading')),
        content=models.TextField(blank=True, verbose_name=_('Content')),
    )

    class Meta():
        verbose_name = _("Block")
        verbose_name_plural = _("Blocks")

    @property
    def body(self):
        return self.content

    def natural_key(self):
        return (self.code,)

    def __str__(self):
        return self.code or self.heading or self.id


class Variable(models.Model):
    code = models.CharField(_('Code'), max_length=64, unique=True)
    value = models.TextField(_('Value'), max_length=5000, blank=True)

    class Meta:
        verbose_name = _("Variable")
        verbose_name_plural = _("Variables")

    def __str__(self):
        return self.code
