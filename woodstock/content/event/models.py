from django.db import models
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from woodstock.models import Event

class NextEventsContent(models.Model):
    count = models.IntegerField(default=5)
    
    class Meta:
        abstract = True
        verbose_name = 'Next Events Content'
        verbose_name_plural = 'Next Events Contents'
    
    def render(self, **kwargs):
        events = Event.objects.pending()[0:self.count]
        return render_to_string('content/woodstock/next_events.html',{'events':events})