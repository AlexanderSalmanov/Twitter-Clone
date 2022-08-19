from django.views.generic import TemplateView

class Hello(TemplateView):
    template_name = 'hello.html'
