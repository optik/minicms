from django import template
from django.core import urlresolvers
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from minicms.models import Page, Block, Variable


register = template.Library()


class ContentSectionNode(template.Node):
    def __init__(self, name):
        self.name = name.strip('"\'')

    def render(self, context):
        page = context.get('page')
        return page.get_content_section(self.name)


@register.tag("content_section")
def do_content_section(parser, token):
    # page = context.get('page', None)
    args = token.split_contents()
    return ContentSectionNode(args[1])


@register.simple_tag(takes_context=True)
def nav_index(context, root_page=None, current_page=None, depth=1):
    if root_page is None:
        root_page = Page.objects.get_info(is_homepage=True)
    elif not isinstance(root_page, Page):
        kwargs = {'id': root_page} if isinstance(root_page, int) else {'code': root_page}
        root_page = Page.objects.get_info(**kwargs)

    child_pages_info = [info for info in Page.objects.registry if info.parent_id == root_page.id]
    html = "\n"
    # TODO: rework to use indexes
    for info in child_pages_info:
        url = urlresolvers.reverse('minicms:page', kwargs={'path': info.path})
        html += '<li><a href="' + url + '">' + info.title + '</a></li>'
    return html


@register.simple_tag(takes_context=True)
def page_url(context, *args, **kwargs):
    info = Page.objects.get_info(**kwargs)
    return urlresolvers.reverse('cms_page', kwargs={'path': info.path})


@register.simple_tag(takes_context=True)
def cms_block(context, code, heading=None):
    request = context.get('request')
    staff = request and request.user.is_authenticated() and request.user.is_staff

    if staff:
        html = '<div data-cms-block="%s">{0}{1}</div>' % code
    else:
        html = "{0}{1}"
    try:
        block = Block.objects.translated().get(code=code)
        heading = "<{0}>{1}</{0}>".format(heading, block.heading) if heading and block.heading else ""
        return mark_safe(html.format(heading, block.content))
    except Block.DoesNotExist:
        return mark_safe(html.format("", _("CMS Block '%s' not found") % code if staff else ""))


@register.simple_tag(takes_context=True)
def cms_var(context, code):
    request = context.get('request')
    staff = request and request.user.is_authenticated() and request.user.is_staff

    try:
        var = Variable.objects.get(code=code)
        return mark_safe(var.value)
    except Variable.DoesNotExist:
        return _("CMS Variable %s not found") % code if staff else ""


@register.simple_tag()
def page_trail(page):
    """Generate page hierarchy trail aka breadcrumbs.

    Args:
        page (mixed): Page instance, code (string) or ID (int)
    """

    def _append_trail(html, page_id):
        info = Page.objects.get_info(id=page_id)
        url = urlresolvers.reverse('minicms:page', kwargs={'path': info.path})
        html = '<a href="' + url + '">' + info.title + '</a>\n' + html
        if info.parent_id:
            html = _append_trail(html, info.parent_id)
        return html

    if isinstance(page, Page):
        page_id = page.id
    elif isinstance(page, str):
        page_id = Page.objects.get_info(code=page).id
    else:
        page_id = page
    return _append_trail('', page_id)


@register.simple_tag(takes_context=True)
def page_active(context, **kwargs):
    matches = False
    try:
        info = Page.objects.get_info(**kwargs)
        resolved = urlresolvers.resolve(context.get('request').path)
        matches = resolved.url_name == 'minicms:page' and resolved.kwargs.path == info.path
    except Exception as e:
        print('Could not resolve path or get page info. Fail reason: %s' % e)
        pass
    return ' active' if matches else ''


@register.simple_tag(takes_context=True)
def cms_metadata(context, page):
    if not isinstance(page, Page):
        try:
            page = Page.objects.get(code=page)
        except Page.DoesNotExist:
            pass
    if isinstance(page, Page):
        context['meta_title'] = page.meta_title
        context['meta_keywords'] = page.meta_keywords
        context['meta_description'] = page.meta_description
    return ""


@register.filter
def or_cms_var(val, cmsvar):
    if not val:
        if not isinstance(cmsvar, Variable):
            try:
                cmsvar = Variable.objects.get(code=cmsvar)
            except Variable.DoesNotExist:
                pass
        if isinstance(cmsvar, Variable):
            return mark_safe(cmsvar.value)
    return val
