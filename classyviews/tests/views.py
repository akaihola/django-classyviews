from classyviews import ClassyView

class test(ClassyView):
    template_name = 'classyviews/tests/test.html'
    def GET(self, request, *args, **kwargs):
        return {'variable': 'value'}

