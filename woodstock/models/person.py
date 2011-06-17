from django.contrib import admin
from django.contrib.auth import login as auth_login, authenticate
from django.db import models
from django.utils.translation import ugettext_lazy as _

from pennyblack.options import NewsletterReceiverMixin

from woodstock import settings
from woodstock.models.extendable import ExtendableMixin

import datetime

#-----------------------------------------------------------------------------
# Person
#-----------------------------------------------------------------------------
class Person(models.Model, NewsletterReceiverMixin, ExtendableMixin):
    salutation = models.ForeignKey('woodstock.Salutation', null=True)
    firstname = models.CharField(verbose_name=_('Firstname'), max_length=100)
    surname = models.CharField(verbose_name=_('Surname'), max_length=100)
    email = models.EmailField(verbose_name=_('E-Mail'), unique=settings.PERSON_EMAIL_UNIQUE)
    password = models.CharField(verbose_name=_('Password'),max_length=100, blank=True)
    is_active = models.BooleanField(verbose_name=_('Active'), default=False)
    last_login = models.DateTimeField(_('last login'), null=True, blank=True)
    language = models.CharField(max_length=5, choices=settings.LANGUAGES,
        default=settings.LANGUAGE_CODE, blank=True)
    
    # used for authentication
    is_staff = False
    is_superuser = False
    
    class Meta:
        abstract = True
    
    def __unicode__(self):
        return self.full_name()
    
    def full_name(self):
        """Creates a full name"""
        return u"%s %s" % (self.surname, self.firstname)
    
    def check_password(self, raw_password):
        return raw_password == self.password
    
    def set_password(self, password):
        self.password = password
        self.save()
    
    def is_authenticated(self):
        """
        Always return True. This is a way to tell if the user has been
        authenticated in templates.
        """
        return True
    
    def on_landing(self, request):
        user = authenticate(user=self)
        if user:
            auth_login(request, user)
    
    def activate(self):
        self.is_active = True
        self.save()
