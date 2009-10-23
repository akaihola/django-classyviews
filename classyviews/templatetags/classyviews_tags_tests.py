from django.test import TestCase
from django.template import Template, Context
from classyviews import ClassyView

class MyView(ClassyView):
    def GET(self, request):
        return {'myvar': u'myval'}

class Templates(TestCase):

    def test_with_view_context(self):
        class request:
            method = 'GET'
        template = Template('{% load classyviews_tags %}'
                            '{% with_view_context MyView %}'
                            '{{ myvar }}'
                            '{% end_with_view_context %}')
        context = {'request': request, 'MyView': MyView}
        result = template.render(Context(context))
        self.assertEqual(result, u'myval')
