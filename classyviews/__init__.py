from django.http import \
    HttpResponse, HttpResponseRedirect, HttpResponseNotAllowed
from django.template import RequestContext
from django.template.loader import render_to_string


class ClassyView(HttpResponse):
    """
    @@@ TODO: Apparently not compatible with caching! Must use
    add_never_cache_headers() for now.

    >>> class MyView(ClassyView):
    ...     def GET(self, request): return {}
    >>> class request:
    ...     method = 'GET'
    >>> print unicode(MyView(request, _render=False)).strip()
    Content-Type: text/html; charset=utf-8
    >>> request.method = 'POST'
    >>> print unicode(MyView(request, _render=False)).strip()
    Content-Type: text/html; charset=utf-8
    Allow: GET

    >>> class RedirView(ClassyView):
    ...     def POST(self, request):
    ...         return HttpResponseRedirect('/elsewhere/')
    >>> print unicode(RedirView(request, _render=False)).strip()
    Content-Type: text/html; charset=utf-8
    Location: /elsewhere/
    """
    template_name = 'default.html'
    _http_methods = (
        'GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'TRACE', 'CONNECT')

    def __init__(self, request, *args, **kwargs):
        self.request = request
        render = kwargs.pop('_render', True)
        try:
            handler = getattr(self, request.method)
        except AttributeError:
            result = HttpResponseNotAllowed(
                [method for method in self._http_methods
                 if hasattr(self, method)])
        else:
            result = handler(request, *args, **kwargs)
        if isinstance(result, HttpResponse):
            self.__class__ = result.__class__
            self.__dict__ = result.__dict__
        else:
            self._context = result
            if render:
                content = self._render(*args, **kwargs)
            else:
                content = ''
            super(ClassyView, self).__init__(content)

    def _render(self, *args, **kwargs):
        return render_to_string(self.template_name,
                                self._context,
                                RequestContext(self.request))

    def set_response(self, cls, *args):
        self.__class__ = cls
        self.__init__(*args)

    def __setstate__(self, state):
        """Unpickle given dictionary into :attr:`__dict__`

        Note that the :attr:`_context` attribute is lost when
        pickling.
        """
        self.__dict__ = state

    def __getstate__(self):
        """Strip the :attr:`_context` attribute when pickling

        The context can include forms which are not picklable.
        """
        return dict((k, v) for k, v in self.__dict__.iteritems()
                    if k != '_context')
