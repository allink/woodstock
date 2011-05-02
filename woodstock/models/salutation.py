from django.contrib import admin
from django.db import models
from django.utils import translation
from django.utils.translation import ugettext_lazy as _

from woodstock import settings

#-----------------------------------------------------------------------------
# Salutation
#-----------------------------------------------------------------------------
class SalutationManager(models.Manager):
    def localized(self):
        """
        Returns a queryset with all salutations aviable in the current language
        """
        return self.filter(language=translation.get_language())
    
    def get_or_add(self, text, language=None):
        try:
            return self.get(text__iexact=text)
        except:
            pass
        try:
            return self.filter(language=language).get(text__is=text)
        except:
            pass
        return self.create(text=text, language=language)

class Salutation(models.Model):
    text = models.CharField(max_length=20)
    gender = models.IntegerField(choices=((0,_('unisex')),(1,_('male')),(2,_('female'))), default=0)
    language = models.CharField(max_length=6, verbose_name=_('Language'), choices=settings.LANGUAGES)
    
    objects = SalutationManager()
    class Meta:
        verbose_name = 'Salutation'
        verbose_name_plural = 'Salutations'
        app_label = 'woodstock'
    
    def __unicode__(self):
        return self.text


class SalutationAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'gender')
