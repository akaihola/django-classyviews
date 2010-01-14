from django.test import TestCase, Client
from django.conf import settings

from classyviews import ClassyView

def make_request(method='GET'):
    class Request: pass
    r = Request()
    r.method = method
    return r

class ClassyViewTests(TestCase):

    def setUp(self):
        self.old_root_urlconf = settings.ROOT_URLCONF
        settings.ROOT_URLCONF = 'classyviews.tests.urls'

    def tearDown(self):
        settings.ROOT_URLCONF = self.old_root_urlconf

    def test_01_no_get_handler(self):
        v = ClassyView(make_request())
        self.assertEqual(v.status_code, 405)

    def test_02_get(self):
        class V(ClassyView):
            template_name = 'classyviews/tests/test.html'
            def GET(self, request, *args, **kwargs):
                return {'variable': 'value'}
        v = V(make_request())
        self.assertEqual(v.status_code, 200)
        self.assertEqual(v.content, 'variable == value\n')
        self.assertEqual(v._context, {'variable': 'value'})

    def test_03_testclient(self):
        c = Client(urlconf='classyviews.tests.urls')
        response = c.get('/classyviews/tests/test/')
        self.assertTrue('variable' in response.context)
        self.assertEqual([c.get('variable') for c in response.context],
                         ['value', None, None, None, None, None, None,
                          None, None])
        self.assertEqual(response.content, 'variable == value\n')
