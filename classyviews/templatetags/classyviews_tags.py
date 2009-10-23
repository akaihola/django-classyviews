from django import template
register = template.Library()

from django.core.urlresolvers import \
    get_callable, get_mod_func, ViewDoesNotExist

class WithViewContextNode(template.Node):
    def __init__(self, view, nodelist):
        self.view = view
        self.nodelist = nodelist

    def __repr__(self):
        return "<WithViewContextNode>"

    def render(self, context):
        view = self.view.resolve(context)
        if not callable(view):
            try:
                view = get_callable(view)
            except ImportError, e:
                mod_name, _ = get_mod_func(view)
                raise ViewDoesNotExist(
                    "Could not import %s. Error was: %s" % (mod_name, str(e)))
            except AttributeError, e:
                mod_name, func_name = get_mod_func(view)
                raise ViewDoesNotExist("Tried %s in module %s. Error was: %s" %
                                       (func_name, mod_name, str(e)))
        response = view(context['request'], _render=False)
        context.push()
        context.update(response.context)
        output = self.nodelist.render(context)
        context.pop()
        return output

@register.tag
def with_view_context(parser, token):
    """
    Calls a class-based view, but instead of rendering a template, only
    requests the context from the view and uses it inside of this block for
    caching and easy access.

    For example::

        {% with_view_context "myapp.views.MyView" %}
          {% include "a-template-using-MyView-context.html" %}
        {% endwith %}
    """
    bits = list(token.split_contents())
    if len(bits) != 2:
        raise TemplateSyntaxError("%r expects view as its only argument" %
                                  bits[0])
    view = parser.compile_filter(bits[1])
    if isinstance(view, basestring) and not view:
        raise TemplateSyntaxError(
                "%r tag doesn't permit an empty view name" % bits[0])
    nodelist = parser.parse(('end_with_view_context',))
    parser.delete_first_token()
    return WithViewContextNode(view, nodelist)
