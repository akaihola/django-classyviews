from django.conf.urls.defaults import *

urlpatterns = patterns(
    '',

    url(r'^classyviews/tests/test/$',
        'classyviews.tests.views.test',
        name='classyviews-tests-root'),

    #url(r'^', include(settings.ROOT_URLCONF)),
)
