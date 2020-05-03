from django.template import Context, Template
from django.test import TestCase

from minicms.models import Variable


class TemplateTagsTestCase(TestCase):
    def setUp(self):
        self.var = Variable.objects.create(code='test_var', value='bar')
        self.var2 = Variable.objects.create(code='other_var', value='xyz')

    def test_cms_var_tag(self):
        "cms_var tag correctly renders CmsVariable value"
        out = Template("{% load minicms %}foo{% cms_var 'test_var' %}baz").render(Context())
        self.assertEqual(out, 'foobarbaz')

    def test_cms_var_tag_as_variable(self):
        "cms_var tag output can be assigned to context variable"
        out = Template("{% load minicms %}{% cms_var 'test_var' as context_var %}foo{{ context_var }}baz").render(Context())
        self.assertEqual(out, 'foobarbaz')

    def test_cms_var_tag_from_context_variable(self):
        "cms_var tag accepts context variable as code argument"
        ctx = {'cms_var_code': 'test_var'}
        out = Template("{% load minicms %}foo{% cms_var cms_var_code %}baz").render(Context(ctx))
        self.assertEqual(out, 'foobarbaz')

    def test_cms_var_tag_from_context_variable_with_filters(self):
        "cms_var tag accepts context variable with filters as code argument"

        out = Template("{% load minicms %}foo{% cms_var no_such_var|default:'other_var' %}baz").render(Context())
        self.assertEqual(out, 'fooxyzbaz')

        ctx = {'cms_var_code': 'OTHER_VAR'}
        out = Template("{% load minicms %}foo{% cms_var cms_var_code|lower %}baz").render(Context(ctx))
        self.assertEqual(out, 'fooxyzbaz')
