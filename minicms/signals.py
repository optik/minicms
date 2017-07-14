from collections import OrderedDict
from lxml import etree
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from django.utils.translation import get_language
from minicms.models import Page, PageTranslation


@receiver(post_save, sender=Page)
def page_post_save(sender, instance, **kwargs):
    """ Reload registry for the current language each time a page is created
    or modified.
    """
    print('page post save')
    Page.objects.reload_registry()


@receiver(post_save, sender=PageTranslation)
def page_translation_post_save(sender, instance, **kwargs):
    """ Reload registry for the current language each time a page is created
    or modified.
    """
    print('page trans post save')
    Page.objects.reload_registry()


@receiver(pre_save, sender=PageTranslation)
def page_translation_pre_save(sender, instance, **kwargs):
    """ Process page content before saving.
    1. Make sure the content is broken down into sections and
    contained in a single 'article' node
    TODO: badly needs a test
    """

    def xstr(s):
        return '' if s is None else str(s)

    page = instance.master

    # 1. Create slug if none
    if instance.slug is None and not page.is_homepage:
        instance.slug = slugify(instance.title)

    # 2. Create slug if none
    tree = instance.html_tree  # XXX: should be implemented here?
    section_keys = page.get_template_section_keys()
    section_content = OrderedDict([('main', xstr(tree.text).lstrip())])
    for node in tree:
        child_content = [etree.tostring(child, encoding="unicode") for child in node.iterchildren()]
        node_content = (xstr(node.text) + ''.join(child_content)).strip()
        section_key = node.attrib.get('data-section-id', None)
        if node.tag == 'section' and section_key in section_keys:
            if section_key in section_content:
                section_content[section_key] += node_content
            else:
                section_content.update({section_key: node_content})
        else:
            section_content['main'] += node_content
        section_content['main'] += xstr(node.tail)

    # combine extracted sections into final page content
    content = ""
    for key in section_keys:
        content += '<section data-section-id="%s">%s</section>\n' % (key, section_content.get(key, ""))
    instance.content = content
