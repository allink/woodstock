from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.template.loader import render_to_string


class LoginContent(models.Model):
    class Meta:
        abstract = True
        verbose_name = 'Login Content'
        verbose_name_plural = 'Login Contents'

    @classmethod
    def initialize_type(cls, login_form=None):
        if not login_form:
            raise ImproperlyConfigured('You have to add specify a login_form')
        cls.login_form = login_form

    def render(self, request):
        if request.method == 'POST':
            login_form = self.login_form(request)
            # todo: not yet finished, should login the user if possible
        else:
            login_form = self.login_form()
        return render_to_string('content/woodstock/login.html', {'login_form': login_form})
